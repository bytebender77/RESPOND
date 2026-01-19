"""Qdrant indexing utilities for RESPOND."""

from qdrant_client.models import PointStruct

from config.settings import settings
from src.qdrant.client import get_qdrant_client
from src.utils.logger import get_logger

_logger = get_logger("qdrant.indexer")


def upsert_point(
    collection: str,
    point_id: str,
    vector: list[float],
    payload: dict,
) -> str:
    """Upsert a single point into a collection.
    
    Args:
        collection: Collection name.
        point_id: Unique point identifier.
        vector: Embedding vector (must match DEFAULT_VECTOR_SIZE).
        payload: Point payload/metadata.
    
    Returns:
        The inserted point_id.
    
    Raises:
        ValueError: If vector length doesn't match expected size.
    """
    expected_size = settings.DEFAULT_VECTOR_SIZE
    if len(vector) != expected_size:
        raise ValueError(
            f"Vector length {len(vector)} doesn't match expected size {expected_size}"
        )
    
    client = get_qdrant_client()
    
    point = PointStruct(
        id=point_id,
        vector=vector,
        payload=payload,
    )
    
    client.upsert(
        collection_name=collection,
        points=[point],
    )
    
    _logger.debug(f"Upserted point {point_id} to {collection}")
    return point_id
