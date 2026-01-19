"""Qdrant client wrapper for RESPOND."""

from qdrant_client import QdrantClient

from config.settings import settings
from src.utils.logger import get_logger

_logger = get_logger("qdrant.client")
_client: QdrantClient | None = None


def get_qdrant_client() -> QdrantClient:
    """Get singleton Qdrant client instance.
    
    Returns:
        Configured QdrantClient instance.
    """
    global _client
    
    if _client is None:
        _logger.info(f"Connecting to Qdrant at {settings.QDRANT_URL}")
        _client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
        )
        _logger.info("Qdrant client initialized")
    
    return _client
