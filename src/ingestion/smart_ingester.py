"""Smart Incident Ingester with Auto-Deduplication for RESPOND.

This module implements Phase 11.1: Auto Deduplication + Auto Reinforcement.
Before inserting a new incident, it searches for similar incidents and either:
- Reinforces an existing incident if similarity >= 0.80
- Creates a new incident otherwise
"""

from src.ingestion.incident_ingester import IncidentIngester
from src.search.hybrid_search import HybridSearcher
from src.memory.memory_manager import MemoryManager
from src.utils.logger import get_logger

_logger = get_logger("ingestion.smart")

# Similarity threshold for deduplication
DEDUP_SIMILARITY_THRESHOLD = 0.70

# Time window for deduplication (in hours)
DEDUP_TIME_WINDOW_HOURS = 2


class SmartIncidentIngester:
    """Smart ingester that auto-deduplicates similar incidents.
    
    Behavior:
    1. Embed incoming incident text
    2. Search for similar incidents in last 2 hours (same zone if provided)
    3. If top result similarity >= 0.80: reinforce existing incident
    4. Otherwise: insert as new incident
    """

    def __init__(self):
        self._basic_ingester = IncidentIngester()
        self._searcher = HybridSearcher()
        self._memory_manager = MemoryManager()

    def ingest(self, data: dict) -> dict:
        """Ingest an incident with auto-deduplication.
        
        Args:
            data: Incident data with required keys: text, source_type.
        
        Returns:
            Dict with:
                - incident_id: ID of the incident (new or existing)
                - message: Description of action taken
                - deduplicated: True if reinforced existing, False if new
                - similarity: (optional) Similarity score if deduplicated
        
        Raises:
            ValueError: If validation fails.
        """
        text = data.get("text", "")
        source_type = data.get("source_type", "")
        zone_id = data.get("zone_id")
        
        # Step 1: Validate input (reuse validation from basic ingester)
        self._basic_ingester._validate(data)
        
        # Step 2: Search for similar incidents in last 2 hours
        _logger.info(f"Searching for duplicates: zone={zone_id}, text='{text[:50]}...'")
        
        similar_incidents = self._searcher.search_incidents(
            query=text,
            limit=3,
            last_hours=DEDUP_TIME_WINDOW_HOURS,
            zone_id=zone_id,
        )
        
        # Step 3: Check if top result is above threshold
        if similar_incidents:
            top_result = similar_incidents[0]
            similarity = top_result["score"]
            
            _logger.info(f"Top match: id={top_result['id'][:8]}..., similarity={similarity:.3f}")
            
            if similarity >= DEDUP_SIMILARITY_THRESHOLD:
                # Reinforce existing incident instead of creating new
                existing_id = top_result["id"]
                
                _logger.info(
                    f"DEDUP: Similarity {similarity:.3f} >= {DEDUP_SIMILARITY_THRESHOLD}, "
                    f"reinforcing incident {existing_id[:8]}..."
                )
                
                # Call reinforce on the existing incident
                reinforce_result = self._memory_manager.reinforce(
                    incident_id=existing_id,
                    new_source_type=source_type,
                    new_text=text,
                )
                
                return {
                    "incident_id": existing_id,
                    "message": "Incident reinforced (deduplicated)",
                    "deduplicated": True,
                    "similarity": round(similarity, 4),
                    "new_confidence": reinforce_result["new_confidence"],
                }
        
        # Step 4: No similar incident found, insert normally
        _logger.info("No duplicate found, creating new incident")
        incident_id = self._basic_ingester.ingest(data)
        
        return {
            "incident_id": incident_id,
            "message": "Incident ingested successfully",
            "deduplicated": False,
        }
