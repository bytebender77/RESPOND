"""Qdrant search utilities for RESPOND."""

from qdrant_client.models import Filter

from src.qdrant.client import get_qdrant_client
from src.utils.logger import get_logger

_logger = get_logger("qdrant.searcher")


def search(
    collection: str,
    query_vector: list[float],
    limit: int = 10,
    qdrant_filter: Filter | None = None,
) -> list[dict]:
    """Perform semantic search on a collection.
    
    Args:
        collection: Collection name to search.
        query_vector: Query embedding vector.
        limit: Maximum results to return.
        qdrant_filter: Optional Qdrant filter object.
    
    Returns:
        List of dicts with id, score, and payload.
    """
    client = get_qdrant_client()
    
    results = client.query_points(
        collection_name=collection,
        query=query_vector,
        limit=limit,
        query_filter=qdrant_filter,
    ).points
    
    _logger.debug(f"Search in {collection} returned {len(results)} results")
    
    return [
        {
            "id": hit.id,
            "score": hit.score,
            "payload": hit.payload,
        }
        for hit in results
    ]
