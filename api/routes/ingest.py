"""Ingest routes for RESPOND API."""

from fastapi import APIRouter, HTTPException

from api.schemas.request_models import IncidentIngestRequest
from api.schemas.response_models import IngestResponse
from src.ingestion import SmartIncidentIngester
from src.utils.logger import get_logger

router = APIRouter(prefix="/ingest", tags=["ingest"])
_logger = get_logger("api.ingest")


@router.post("/incident", response_model=IngestResponse)
async def ingest_incident(request: IncidentIngestRequest):
    """Ingest a new incident report with auto-deduplication.
    
    The system automatically detects duplicates:
    - Searches for similar incidents in the last 2 hours (same zone if provided)
    - If similarity >= 0.80: reinforces existing incident instead of creating new
    - Otherwise: creates a new incident normally
    
    Args:
        request: Incident data.
    
    Returns:
        IngestResponse with incident_id and deduplicated status.
    """
    try:
        ingester = SmartIncidentIngester()
        
        # Convert request to dict
        data = request.model_dump(exclude_none=True)
        
        # Smart ingest with auto-deduplication
        result = ingester.ingest(data)
        
        _logger.info(
            f"API ingested incident {result['incident_id'][:8]}... "
            f"(deduplicated={result.get('deduplicated', False)})"
        )
        
        return IngestResponse(
            incident_id=result["incident_id"],
            message=result["message"],
        )
    
    except ValueError as e:
        _logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        _logger.error(f"Ingest error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

