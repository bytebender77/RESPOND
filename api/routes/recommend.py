"""Recommendation routes for RESPOND API."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.recommendation import ActionRecommender
from src.utils.logger import get_logger

router = APIRouter(prefix="/recommend", tags=["recommend"])
_logger = get_logger("api.recommend")


class RecommendActionsRequest(BaseModel):
    """Request model for action recommendations."""
    query: str
    limit: int = 5
    zone_id: str | None = None


@router.post("/actions")
async def recommend_actions(request: RecommendActionsRequest):
    """Generate action recommendations based on incidents.
    
    Args:
        request: Query and filter parameters.
    
    Returns:
        Dict with query, actions, and evidence_used.
    """
    try:
        recommender = ActionRecommender()
        
        result = recommender.recommend_actions(
            query=request.query,
            limit=request.limit,
            zone_id=request.zone_id,
        )
        
        _logger.info(f"Generated {len(result['actions'])} action recommendations")
        
        return result
    
    except ValueError as e:
        _logger.error(f"Recommendation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        _logger.error(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
