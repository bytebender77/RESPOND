"""Hybrid semantic search for RESPOND."""

from config.qdrant_config import SITUATION_REPORTS
from src.embeddings.text_embedder import TextEmbedder
from src.qdrant.searcher import search
from src.search.filters import (
    build_status_filter,
    build_urgency_filter,
    build_zone_filter,
    build_time_filter,
    build_geo_filter,
    combine_filters,
)
from src.memory.decay import apply_decay
from src.evidence.tracer import extract_evidence
from src.utils.logger import get_logger

_logger = get_logger("search.hybrid")


class HybridSearcher:
    """Hybrid semantic search with operational filters, time decay, and evidence."""

    def __init__(self):
        self._embedder = TextEmbedder()

    def search_incidents(
        self,
        query: str,
        limit: int = 10,
        zone_id: str | None = None,
        urgency: str | None = None,
        status: str | None = None,
        last_hours: int | None = None,
        center: dict | None = None,
        radius_km: float | None = None,
    ) -> list[dict]:
        """Search incidents with semantic similarity, filters, decay, and evidence.
        
        Args:
            query: Search query text.
            limit: Maximum results to return.
            zone_id: Filter by zone ID.
            urgency: Filter by urgency level.
            status: Filter by status.
            last_hours: Filter to incidents within last N hours.
            center: Geo center point {"lat": float, "lon": float}.
            radius_km: Radius in kilometers for geo search.
        
        Returns:
            List of dicts with id, score, payload, final_score, decay_factor, 
            age_seconds, and evidence.
        """
        # Generate query embedding
        query_vector = self._embedder.embed_text(query)
        
        # Build filters
        filters = [
            build_status_filter(status),
            build_urgency_filter(urgency),
            build_zone_filter(zone_id),
            build_time_filter(last_hours),
            build_geo_filter(center, radius_km),
        ]
        combined_filter = combine_filters(filters)
        
        # Execute search
        results = search(
            collection=SITUATION_REPORTS,
            query_vector=query_vector,
            limit=limit,
            qdrant_filter=combined_filter,
        )
        
        # Apply decay, extract evidence, and rerank
        reranked = []
        for r in results:
            timestamp_unix = r["payload"].get("timestamp_unix")
            decay_info = apply_decay(r["score"], timestamp_unix)
            evidence = extract_evidence(r["payload"])
            
            reranked.append({
                "id": r["id"],
                "score": r["score"],
                "payload": r["payload"],
                "final_score": decay_info["final_score"],
                "decay_factor": decay_info["decay_factor"],
                "age_seconds": decay_info["age_seconds"],
                "evidence": evidence,
            })
        
        # Sort by final_score descending
        reranked.sort(key=lambda x: x["final_score"], reverse=True)
        
        _logger.info(f"Search query='{query[:50]}...' returned {len(reranked)} results (reranked)")
        return reranked
