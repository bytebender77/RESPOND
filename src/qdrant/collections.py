"""Qdrant collection management for RESPOND."""

from qdrant_client.models import (
    Distance,
    VectorParams,
    PayloadSchemaType,
)

from config.settings import settings
from config.qdrant_config import (
    SITUATION_REPORTS,
    DISASTER_EVENTS,
    RESOURCE_DEPLOYMENTS,
    HISTORICAL_PATTERNS,
)
from src.qdrant.client import get_qdrant_client
from src.utils.logger import get_logger

_logger = get_logger("qdrant.collections")

# All collection names
ALL_COLLECTIONS = [
    SITUATION_REPORTS,
    DISASTER_EVENTS,
    RESOURCE_DEPLOYMENTS,
    HISTORICAL_PATTERNS,
]

# Payload fields to index for filtering
PAYLOAD_INDEX_SCHEMA = {
    "timestamp": PayloadSchemaType.KEYWORD,
    "timestamp_unix": PayloadSchemaType.INTEGER,
    "source_type": PayloadSchemaType.KEYWORD,
    "urgency": PayloadSchemaType.KEYWORD,
    "status": PayloadSchemaType.KEYWORD,
    "zone_id": PayloadSchemaType.KEYWORD,
    "confidence_score": PayloadSchemaType.FLOAT,
    "location": PayloadSchemaType.GEO,
}


def collection_exists(name: str) -> bool:
    """Check if a collection exists.
    
    Args:
        name: Collection name.
    
    Returns:
        True if collection exists.
    """
    client = get_qdrant_client()
    collections = client.get_collections().collections
    return any(c.name == name for c in collections)


def create_collection(name: str) -> None:
    """Create a collection with vector config and payload indexes.
    
    Args:
        name: Collection name to create.
    """
    client = get_qdrant_client()
    
    # Map distance string to enum
    distance_map = {
        "Cosine": Distance.COSINE,
        "Euclid": Distance.EUCLID,
        "Dot": Distance.DOT,
    }
    distance = distance_map.get(settings.DEFAULT_DISTANCE, Distance.COSINE)
    
    # Create collection with vector config
    client.create_collection(
        collection_name=name,
        vectors_config=VectorParams(
            size=settings.DEFAULT_VECTOR_SIZE,
            distance=distance,
        ),
    )
    _logger.info(f"Created collection: {name}")
    
    # Create payload indexes for filtering
    _create_payload_indexes(name)


def _create_payload_indexes(name: str) -> None:
    """Create payload indexes for a collection.
    
    Args:
        name: Collection name.
    """
    client = get_qdrant_client()
    
    for field_name, field_type in PAYLOAD_INDEX_SCHEMA.items():
        try:
            client.create_payload_index(
                collection_name=name,
                field_name=field_name,
                field_schema=field_type,
            )
        except Exception as e:
            # Index may already exist
            _logger.debug(f"Index {field_name} may already exist: {e}")
    
    _logger.info(f"Created payload indexes for: {name}")


def setup_all_collections() -> dict:
    """Create all required collections if they don't exist.
    
    Returns:
        Dict with 'created' and 'existing' collection lists.
    """
    created = []
    existing = []
    
    for name in ALL_COLLECTIONS:
        if collection_exists(name):
            _logger.info(f"Collection already exists: {name}")
            existing.append(name)
        else:
            create_collection(name)
            created.append(name)
    
    return {"created": created, "existing": existing}


def ensure_indexes(collection_name: str) -> None:
    """Ensure payload indexes exist for a collection.
    
    Args:
        collection_name: Collection to add indexes to.
    """
    _create_payload_indexes(collection_name)
