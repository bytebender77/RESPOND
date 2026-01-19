"""Memory manager for RESPOND incident lifecycle."""

from config.qdrant_config import SITUATION_REPORTS
from src.qdrant.client import get_qdrant_client
from src.embeddings.text_embedder import TextEmbedder
from src.memory.reinforcement import compute_text_similarity, reinforce_incident
from src.utils.time_utils import utc_now_iso
from src.utils.logger import get_logger

_logger = get_logger("memory.manager")


class MemoryManager:
    """Manages incident memory stored in Qdrant."""

    def __init__(self):
        self._client = get_qdrant_client()
        self._collection = SITUATION_REPORTS
        self._embedder = TextEmbedder()

    def get_incident(self, incident_id: str) -> dict | None:
        """Fetch incident by ID.
        
        Args:
            incident_id: Incident UUID.
        
        Returns:
            Dict with id and payload, or None if not found.
        """
        try:
            results = self._client.retrieve(
                collection_name=self._collection,
                ids=[incident_id],
                with_payload=True,
            )
            
            if not results:
                _logger.debug(f"Incident {incident_id} not found")
                return None
            
            point = results[0]
            return {
                "id": str(point.id),
                "payload": point.payload,
            }
        except Exception as e:
            _logger.error(f"Error fetching incident {incident_id}: {e}")
            return None

    def update_incident_payload(self, incident_id: str, updates: dict) -> bool:
        """Update payload fields for an incident.
        
        Args:
            incident_id: Incident UUID.
            updates: Dict of fields to update.
        
        Returns:
            True if update was successful.
        """
        try:
            # Add updated_at timestamp
            updates["updated_at"] = utc_now_iso()
            
            self._client.set_payload(
                collection_name=self._collection,
                payload=updates,
                points=[incident_id],
            )
            
            _logger.info(f"Updated incident {incident_id}: {list(updates.keys())}")
            return True
        except Exception as e:
            _logger.error(f"Error updating incident {incident_id}: {e}")
            return False

    def reinforce(self, incident_id: str, new_source_type: str, new_text: str) -> dict:
        """Reinforce incident with new evidence.
        
        Args:
            incident_id: Incident UUID.
            new_source_type: Source type of new evidence.
            new_text: Text content of new evidence.
        
        Returns:
            Dict with reinforcement results.
        
        Raises:
            ValueError: If incident not found or invalid input.
        """
        # Fetch incident
        incident = self.get_incident(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")
        
        payload = incident["payload"]
        original_text = payload.get("text", "")
        
        # Compute embeddings
        vec1 = self._embedder.embed_text(original_text)
        vec2 = self._embedder.embed_text(new_text)
        
        # Compute similarity
        similarity = compute_text_similarity(vec1, vec2)
        
        # Apply reinforcement
        updates = reinforce_incident(payload, new_source_type, new_text, similarity)
        
        # Extract meta info before removing it
        meta = updates.pop("_meta")
        
        # Update payload in Qdrant
        self._client.set_payload(
            collection_name=self._collection,
            payload=updates,
            points=[incident_id],
        )
        
        _logger.info(f"Reinforced incident {incident_id}: accepted={meta['accepted']}")
        
        return {
            "incident_id": incident_id,
            "similarity": round(similarity, 4),
            "accepted": meta["accepted"],
            "old_confidence": meta["old_confidence"],
            "new_confidence": meta["new_confidence"],
            "reinforced_count": updates["reinforced_count"],
        }
