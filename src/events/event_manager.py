"""Disaster Event Manager for RESPOND.

Phase 14.1: Event grouping to cluster related incidents.
Groups multiple incidents into disaster event clusters based on semantic similarity.
"""

from datetime import datetime, timezone

from config.qdrant_config import DISASTER_EVENTS, SITUATION_REPORTS
from src.embeddings.text_embedder import TextEmbedder
from src.qdrant.client import get_qdrant_client
from src.qdrant.indexer import upsert_point
from src.qdrant.searcher import search
from src.search.filters import build_zone_filter
from src.utils.ids import generate_uuid
from src.utils.time_utils import utc_now_iso
from src.utils.logger import get_logger

_logger = get_logger("events.manager")

# Similarity threshold for grouping incidents into events
EVENT_SIMILARITY_THRESHOLD = 0.75


class EventManager:
    """Manages disaster event grouping in Qdrant.
    
    Events are clusters of related incidents. When a new incident arrives,
    we check if it matches an existing event (similarity >= 0.75 in same zone).
    If yes, attach it to that event. If no, create a new event.
    """

    def __init__(self):
        self._client = get_qdrant_client()
        self._embedder = TextEmbedder()
        self._collection = DISASTER_EVENTS

    def create_event_from_incident(self, incident_id: str, incident_payload: dict) -> str:
        """Create a new disaster event from an incident.
        
        Args:
            incident_id: UUID of the incident.
            incident_payload: Incident payload data.
        
        Returns:
            Created event_id.
        """
        text = incident_payload.get("text", "")
        zone_id = incident_payload.get("zone_id", "unknown")
        urgency = incident_payload.get("urgency", "medium")
        
        # Generate event title from incident text (first 50 chars)
        title = self._generate_title(text)
        
        # Generate embedding from incident text
        vector = self._embedder.embed_text(text)
        
        now = utc_now_iso()
        now_unix = int(datetime.now(timezone.utc).timestamp())
        
        # Build event payload
        payload = {
            "title": title,
            "zone_id": zone_id,
            "incident_ids": [incident_id],
            "incident_count": 1,
            "urgency_max": urgency,
            "status": "active",
            "created_at": now,
            "updated_at": now,
            "timestamp_unix": now_unix,
        }
        
        # Generate event ID and store
        event_id = generate_uuid()
        upsert_point(
            collection=self._collection,
            point_id=event_id,
            vector=vector,
            payload=payload,
        )
        
        _logger.info(f"Created event {event_id[:8]}... with incident {incident_id[:8]}...")
        return event_id

    def assign_incident_to_event(
        self,
        incident_id: str,
        incident_payload: dict,
    ) -> dict:
        """Assign an incident to an existing event or create new event.
        
        Logic:
        1. Search for events with similar text in same zone
        2. If similarity >= 0.75, attach incident to that event
        3. Otherwise, create a new event
        
        Args:
            incident_id: UUID of the incident.
            incident_payload: Incident payload data.
        
        Returns:
            Dict with event_id, is_new, and similarity (if matched).
        """
        text = incident_payload.get("text", "")
        zone_id = incident_payload.get("zone_id")
        urgency = incident_payload.get("urgency", "medium")
        
        # Search for matching events
        vector = self._embedder.embed_text(text)
        
        # Build filter for same zone
        zone_filter = build_zone_filter(zone_id) if zone_id else None
        
        results = search(
            collection=self._collection,
            query_vector=vector,
            limit=3,
            qdrant_filter=zone_filter,
        )
        
        # Check if any existing event matches
        if results:
            top = results[0]
            similarity = top["score"]
            
            if similarity >= EVENT_SIMILARITY_THRESHOLD:
                # Attach to existing event
                existing_event_id = top["id"]
                existing_payload = top["payload"]
                
                # Update event with new incident
                self._add_incident_to_event(
                    event_id=existing_event_id,
                    incident_id=incident_id,
                    incident_urgency=urgency,
                    existing_payload=existing_payload,
                )
                
                _logger.info(
                    f"Attached incident {incident_id[:8]}... to event {existing_event_id[:8]}... "
                    f"(similarity={similarity:.3f})"
                )
                
                return {
                    "event_id": existing_event_id,
                    "is_new": False,
                    "similarity": similarity,
                }
        
        # No matching event, create new
        event_id = self.create_event_from_incident(incident_id, incident_payload)
        
        return {
            "event_id": event_id,
            "is_new": True,
            "similarity": None,
        }

    def _add_incident_to_event(
        self,
        event_id: str,
        incident_id: str,
        incident_urgency: str,
        existing_payload: dict,
    ) -> None:
        """Add an incident to an existing event.
        
        Args:
            event_id: Event UUID.
            incident_id: Incident UUID to add.
            incident_urgency: Urgency of the incident.
            existing_payload: Current event payload.
        """
        # Get current incident list
        incident_ids = existing_payload.get("incident_ids", [])
        
        # Avoid duplicates
        if incident_id not in incident_ids:
            incident_ids.append(incident_id)
        
        # Determine max urgency
        urgency_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        current_max = existing_payload.get("urgency_max", "low")
        new_max = current_max
        
        if urgency_order.get(incident_urgency, 0) > urgency_order.get(current_max, 0):
            new_max = incident_urgency
        
        # Update payload
        updates = {
            "incident_ids": incident_ids,
            "incident_count": len(incident_ids),
            "urgency_max": new_max,
            "updated_at": utc_now_iso(),
        }
        
        self._client.set_payload(
            collection_name=self._collection,
            payload=updates,
            points=[event_id],
        )

    def get_event(self, event_id: str) -> dict | None:
        """Fetch event by ID.
        
        Args:
            event_id: Event UUID.
        
        Returns:
            Dict with id and payload, or None if not found.
        """
        try:
            results = self._client.retrieve(
                collection_name=self._collection,
                ids=[event_id],
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
            _logger.error(f"Error fetching event {event_id}: {e}")
            return None

    def _generate_title(self, text: str, max_length: int = 60) -> str:
        """Generate event title from incident text.
        
        Args:
            text: Incident text.
            max_length: Maximum title length.
        
        Returns:
            Generated title string.
        """
        # Simple truncation for now
        title = text.strip()
        if len(title) > max_length:
            title = title[:max_length - 3] + "..."
        return title
