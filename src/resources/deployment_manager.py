"""Resource Deployment Manager for RESPOND.

Phase 15.1: Resource deployment memory.
Tracks deployed units and their status for incident response.
"""

from datetime import datetime, timezone

from config.qdrant_config import RESOURCE_DEPLOYMENTS
from src.embeddings.text_embedder import TextEmbedder
from src.qdrant.client import get_qdrant_client
from src.qdrant.indexer import upsert_point
from src.utils.ids import generate_uuid
from src.utils.time_utils import utc_now_iso
from src.utils.logger import get_logger

_logger = get_logger("resources.deployment")

# Valid deployment statuses
DEPLOYMENT_STATUSES = ["assigned", "en_route", "on_site", "completed", "cancelled"]


class DeploymentManager:
    """Manages resource deployments in Qdrant.
    
    Tracks which units are deployed to which incidents and their current status.
    """

    def __init__(self):
        self._client = get_qdrant_client()
        self._embedder = TextEmbedder()
        self._collection = RESOURCE_DEPLOYMENTS

    def create_deployment(
        self,
        action_type: str,
        incident_ids: list[str],
        assigned_unit: str,
        status: str = "assigned",
        zone_id: str = None,
        notes: str = None,
    ) -> dict:
        """Create a new resource deployment.
        
        Args:
            action_type: Type of action (e.g., "DISPATCH_FIRE_UNIT", "EVACUATE_ZONE").
            incident_ids: List of incident UUIDs this deployment addresses.
            assigned_unit: Unit identifier (e.g., "Fire Unit 7", "Ambulance 12").
            status: Initial status (default: "assigned").
            zone_id: Optional zone identifier.
            notes: Optional notes about the deployment.
        
        Returns:
            Dict with deployment_id and details.
        
        Raises:
            ValueError: If validation fails.
        """
        # Validate
        if not action_type or not action_type.strip():
            raise ValueError("action_type is required")
        if not incident_ids or len(incident_ids) == 0:
            raise ValueError("At least one incident_id is required")
        if not assigned_unit or not assigned_unit.strip():
            raise ValueError("assigned_unit is required")
        if status not in DEPLOYMENT_STATUSES:
            raise ValueError(f"status must be one of {DEPLOYMENT_STATUSES}")
        
        now = utc_now_iso()
        now_unix = int(datetime.now(timezone.utc).timestamp())
        
        # Generate embedding from action description
        embed_text = f"{action_type} {assigned_unit}"
        vector = self._embedder.embed_text(embed_text)
        
        # Build payload
        payload = {
            "action_type": action_type,
            "incident_ids": incident_ids,
            "incident_count": len(incident_ids),
            "assigned_unit": assigned_unit,
            "status": status,
            "zone_id": zone_id,
            "notes": notes,
            "timestamp_unix": now_unix,
            "created_at": now,
            "updated_at": now,
        }
        
        # Generate ID and store
        deployment_id = generate_uuid()
        upsert_point(
            collection=self._collection,
            point_id=deployment_id,
            vector=vector,
            payload=payload,
        )
        
        _logger.info(
            f"Created deployment {deployment_id[:8]}... "
            f"({action_type} -> {assigned_unit})"
        )
        
        return {
            "deployment_id": deployment_id,
            "action_type": action_type,
            "assigned_unit": assigned_unit,
            "status": status,
            "incident_count": len(incident_ids),
        }

    def update_deployment_status(
        self,
        deployment_id: str,
        new_status: str,
        notes: str = None,
    ) -> dict:
        """Update the status of a deployment.
        
        Args:
            deployment_id: Deployment UUID.
            new_status: New status value.
            notes: Optional status update notes.
        
        Returns:
            Dict with old_status, new_status, and deployment_id.
        
        Raises:
            ValueError: If deployment not found or invalid status.
        """
        if new_status not in DEPLOYMENT_STATUSES:
            raise ValueError(f"status must be one of {DEPLOYMENT_STATUSES}")
        
        # Fetch current deployment
        deployment = self.get_deployment(deployment_id)
        if not deployment:
            raise ValueError(f"Deployment {deployment_id} not found")
        
        old_status = deployment["payload"].get("status", "unknown")
        
        # Build updates
        updates = {
            "status": new_status,
            "updated_at": utc_now_iso(),
        }
        if notes:
            updates["notes"] = notes
        
        # Update in Qdrant
        self._client.set_payload(
            collection_name=self._collection,
            payload=updates,
            points=[deployment_id],
        )
        
        _logger.info(
            f"Updated deployment {deployment_id[:8]}... "
            f"status: {old_status} -> {new_status}"
        )
        
        return {
            "deployment_id": deployment_id,
            "old_status": old_status,
            "new_status": new_status,
        }

    def get_deployment(self, deployment_id: str) -> dict | None:
        """Fetch deployment by ID.
        
        Args:
            deployment_id: Deployment UUID.
        
        Returns:
            Dict with id and payload, or None if not found.
        """
        try:
            results = self._client.retrieve(
                collection_name=self._collection,
                ids=[deployment_id],
                with_payload=True,
            )
            
            if not results:
                return None
            
            point = results[0]
            return {
                "id": str(point.id),
                "payload": point.payload,
            }
        except Exception as e:
            _logger.error(f"Error fetching deployment {deployment_id}: {e}")
            return None

    def list_active_deployments(self, zone_id: str = None) -> list[dict]:
        """List all active (non-completed) deployments.
        
        Args:
            zone_id: Optional filter by zone.
        
        Returns:
            List of deployment dicts.
        """
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        # Filter for non-completed statuses
        conditions = [
            FieldCondition(
                key="status",
                match=MatchValue(value=status),
            )
            for status in ["assigned", "en_route", "on_site"]
        ]
        
        try:
            # Search with dummy vector (we just want to list)
            dummy_vector = [0.0] * 384
            
            results = self._client.search(
                collection_name=self._collection,
                query_vector=dummy_vector,
                limit=50,
                query_filter=Filter(should=conditions),
                with_payload=True,
            )
            
            deployments = []
            for r in results:
                if zone_id and r.payload.get("zone_id") != zone_id:
                    continue
                deployments.append({
                    "id": str(r.id),
                    "payload": r.payload,
                })
            
            return deployments
        except Exception as e:
            _logger.error(f"Error listing deployments: {e}")
            return []
