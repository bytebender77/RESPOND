"""Setup routes for RESPOND API."""

from fastapi import APIRouter

from src.qdrant.collections import setup_all_collections
from src.qdrant.client import get_qdrant_client
from config.qdrant_config import (
    SITUATION_REPORTS,
    DISASTER_EVENTS,
    RESOURCE_DEPLOYMENTS,
    HISTORICAL_PATTERNS,
)

router = APIRouter(tags=["setup"])


@router.get("/setup")
async def setup_collections():
    """Initialize all Qdrant collections.
    
    Returns:
        Dict with created and existing collection lists.
    """
    result = setup_all_collections()
    return {
        "status": "ok",
        "collections": result,
    }


@router.delete("/reset")
async def reset_collections():
    """Delete and recreate all collections to clear all data.
    
    WARNING: This will delete all incidents!
    
    Returns:
        Dict with reset status.
    """
    client = get_qdrant_client()
    
    collections = [
        SITUATION_REPORTS,
        DISASTER_EVENTS,
        RESOURCE_DEPLOYMENTS,
        HISTORICAL_PATTERNS,
    ]
    
    deleted = []
    for name in collections:
        try:
            client.delete_collection(name)
            deleted.append(name)
        except Exception:
            pass  # Collection might not exist
    
    # Recreate collections
    result = setup_all_collections()
    
    return {
        "status": "ok",
        "deleted": deleted,
        "recreated": result,
    }
