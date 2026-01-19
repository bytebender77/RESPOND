"""Ingest routes for RESPOND API."""

from fastapi import APIRouter, HTTPException

from api.schemas.request_models import IncidentIngestRequest
from api.schemas.response_models import IngestResponse
from src.ingestion import IncidentIngester
from src.utils.logger import get_logger

router = APIRouter(prefix="/ingest", tags=["ingest"])
_logger = get_logger("api.ingest")


@router.post("/incident", response_model=IngestResponse)
async def ingest_incident(request: IncidentIngestRequest):
    """Ingest a new incident report.
    
    Args:
        request: Incident data.
    
    Returns:
        IngestResponse with incident_id.
    """
    try:
        ingester = IncidentIngester()
        
        # Convert request to dict
        data = request.model_dump(exclude_none=True)
        
        # Ingest incident
        incident_id = ingester.ingest(data)
        
        _logger.info(f"API ingested incident {incident_id}")
        
        return IngestResponse(
            incident_id=incident_id,
            message="Incident ingested successfully",
        )
    
    except ValueError as e:
        _logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        _logger.error(f"Ingest error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
