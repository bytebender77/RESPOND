"""Image search routes for RESPOND API.

Search images using text queries via CLIP embeddings.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config.qdrant_config import INCIDENT_IMAGES
from src.embeddings.image_embedder import ImageEmbedder
from src.qdrant.client import get_qdrant_client
from src.utils.logger import get_logger

router = APIRouter(prefix="/search", tags=["images"])
_logger = get_logger("api.image_search")


class ImageSearchRequest(BaseModel):
    """Request model for image search."""
    query: str
    limit: int = 10
    zone_id: str | None = None
    image_type: str | None = None


class ImageSearchResult(BaseModel):
    """Single image search result."""
    image_id: str
    incident_id: str
    image_path: str
    image_type: str
    score: float
    zone_id: str | None = None
    created_at: str | None = None
    incident_text: str | None = None


class ImageSearchResponse(BaseModel):
    """Response model for image search."""
    query: str
    count: int
    results: list[ImageSearchResult]


@router.post("/images", response_model=ImageSearchResponse)
async def search_images(request: ImageSearchRequest):
    """Search images using a text query.
    
    Uses CLIP to embed the text query and find similar images.
    This enables cross-modal search (text -> image).
    
    Args:
        request: Search parameters.
    
    Returns:
        ImageSearchResponse with matching images.
    """
    try:
        # Embed text query using CLIP
        embedder = ImageEmbedder()
        query_vector = embedder.embed_text(request.query)
        
        client = get_qdrant_client()
        
        # Build filter if specified
        filter_conditions = []
        
        if request.zone_id:
            from qdrant_client.models import FieldCondition, MatchValue
            filter_conditions.append(
                FieldCondition(key="zone_id", match=MatchValue(value=request.zone_id))
            )
        
        if request.image_type:
            from qdrant_client.models import FieldCondition, MatchValue
            filter_conditions.append(
                FieldCondition(key="image_type", match=MatchValue(value=request.image_type))
            )
        
        # Build Qdrant filter
        qdrant_filter = None
        if filter_conditions:
            from qdrant_client.models import Filter
            qdrant_filter = Filter(must=filter_conditions)
        
        # Search
        results_obj = client.query_points(
            collection_name=INCIDENT_IMAGES,
            query=query_vector,
            limit=request.limit,
            query_filter=qdrant_filter,
            with_payload=True,
        )
        results = results_obj.points
        # Extract incident IDs to fetch context
        incident_ids = list(set(r.payload.get("incident_id") for r in results_obj.points if r.payload.get("incident_id")))
        
        # Fetch incident details
        incident_map = {}
        if incident_ids:
            try:
                from config.qdrant_config import SITUATION_REPORTS
                incidents = client.retrieve(
                    collection_name=SITUATION_REPORTS,
                    ids=incident_ids,
                    with_payload=["text"],
                )
                for inc in incidents:
                    incident_map[str(inc.id)] = inc.payload.get("text", "")
            except Exception as e:
                _logger.warning(f"Could not fetch incident details: {e}")

        # Format results
        formatted = []
        for r in results_obj.points:
            # Fix image path for frontend serving
            raw_path = r.payload.get("image_path", "")
            if "uploads/" in raw_path:
                # Convert absolute path to relative path
                image_path = "uploads/" + raw_path.split("uploads/")[1]
            else:
                image_path = raw_path
            
            inc_id = r.payload.get("incident_id", "")
            
            formatted.append(ImageSearchResult(
                image_id=str(r.id),
                incident_id=inc_id,
                image_path=image_path,
                image_type=r.payload.get("image_type", "photo"),
                score=r.score,
                zone_id=r.payload.get("zone_id"),
                created_at=r.payload.get("created_at"),
                incident_text=incident_map.get(inc_id),
            ))
        
        _logger.info(f"Image search '{request.query}' returned {len(formatted)} results")
        
        return ImageSearchResponse(
            query=request.query,
            count=len(formatted),
            results=formatted,
        )
    
    except Exception as e:
        _logger.error(f"Image search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/images/incident/{incident_id}")
async def get_incident_images(incident_id: str):
    """Get all images for a specific incident.
    
    Args:
        incident_id: Incident UUID.
    
    Returns:
        List of images for this incident.
    """
    try:
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        client = get_qdrant_client()
        
        # Filter by incident_id
        results = client.scroll(
            collection_name=INCIDENT_IMAGES,
            scroll_filter=Filter(
                must=[
                    FieldCondition(key="incident_id", match=MatchValue(value=incident_id))
                ]
            ),
            limit=50,
            with_payload=True,
            with_vectors=False,
        )
        
        images = []
        for point in results[0]:
            images.append({
                "image_id": str(point.id),
                "image_path": point.payload.get("image_path", ""),
                "image_type": point.payload.get("image_type", "photo"),
                "created_at": point.payload.get("created_at"),
            })
        
        return {
            "incident_id": incident_id,
            "count": len(images),
            "images": images,
        }
    
    except Exception as e:
        _logger.error(f"Get incident images error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
