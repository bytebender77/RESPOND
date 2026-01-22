"""Qdrant indexing utilities for RESPOND."""

from qdrant_client.models import PointStruct

from config.qdrant_config import INCIDENT_IMAGES
from src.qdrant.client import get_qdrant_client
from src.qdrant.collections import IMAGE_VECTOR_SIZE, TEXT_VECTOR_SIZE
from src.utils.logger import get_logger

_logger = get_logger("qdrant.indexer")

# Collection to vector size mapping
COLLECTION_VECTOR_SIZES = {
    INCIDENT_IMAGES: IMAGE_VECTOR_SIZE,  # 512 for CLIP
}


def get_expected_vector_size(collection: str) -> int:
    """Get expected vector size for a collection.
    
    Args:
        collection: Collection name.
    
    Returns:
        Expected vector dimensions.
    """
    return COLLECTION_VECTOR_SIZES.get(collection, TEXT_VECTOR_SIZE)


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
        vector: Embedding vector.
        payload: Point payload/metadata.
    
    Returns:
        The inserted point_id.
    
    Raises:
        ValueError: If vector length doesn't match expected size for collection.
    """
    expected_size = get_expected_vector_size(collection)
    if len(vector) != expected_size:
        raise ValueError(
            f"Vector length {len(vector)} doesn't match expected size {expected_size} "
            f"for collection {collection}"
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

