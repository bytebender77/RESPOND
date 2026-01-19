"""Search routes for RESPOND API."""

from fastapi import APIRouter, HTTPException

from api.schemas.request_models import IncidentSearchRequest
from api.schemas.response_models import SearchResponse, SearchResultItem
from src.search import HybridSearcher
from src.utils.logger import get_logger

router = APIRouter(prefix="/search", tags=["search"])
_logger = get_logger("api.search")


@router.post("/incidents", response_model=SearchResponse)
async def search_incidents(request: IncidentSearchRequest):
    """Search incidents with semantic similarity, filters, decay, and evidence.
    
    Args:
        request: Search parameters.
    
    Returns:
        SearchResponse with reranked results including evidence.
    """
    try:
        searcher = HybridSearcher()
        
        # Execute search (includes decay reranking and evidence)
        results = searcher.search_incidents(
            query=request.query,
            limit=request.limit,
            zone_id=request.zone_id,
            urgency=request.urgency,
            status=request.status,
            last_hours=request.last_hours,
            center=request.center,
            radius_km=request.radius_km,
        )
        
        # Convert to response model
        result_items = [
            SearchResultItem(
                id=str(r["id"]),
                score=float(r["score"]),
                payload=r["payload"],
                final_score=float(r["final_score"]),
                decay_factor=float(r["decay_factor"]),
                age_seconds=int(r["age_seconds"]),
                evidence=r["evidence"],
            )
            for r in results
        ]
        
        _logger.info(f"API search returned {len(result_items)} results")
        
        return SearchResponse(
            count=len(result_items),
            results=result_items,
        )
    
    except ValueError as e:
        _logger.error(f"Search validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        _logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
