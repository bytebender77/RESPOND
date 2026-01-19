"""Memory routes for RESPOND API."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config.qdrant_config import SUPPORTED_SOURCE_TYPES
from src.memory import MemoryManager
from src.memory.evolution import is_valid_transition, ALLOWED_STATUS_TRANSITIONS
from src.utils.logger import get_logger

router = APIRouter(prefix="/memory", tags=["memory"])
_logger = get_logger("api.memory")


# Request/Response Models
class StatusUpdateRequest(BaseModel):
    """Request model for status update."""
    status: str


class StatusUpdateResponse(BaseModel):
    """Response model for status update."""
    incident_id: str
    old_status: str
    new_status: str
    message: str


class ReinforceRequest(BaseModel):
    """Request model for reinforcement."""
    source_type: str
    text: str


class ReinforceResponse(BaseModel):
    """Response model for reinforcement."""
    incident_id: str
    similarity: float
    accepted: bool
    old_confidence: float
    new_confidence: float
    reinforced_count: int


@router.patch("/incident/{incident_id}/status", response_model=StatusUpdateResponse)
async def update_incident_status(incident_id: str, request: StatusUpdateRequest):
    """Update incident status with evolution rules.
    
    Args:
        incident_id: Incident UUID.
        request: New status.
    
    Returns:
        StatusUpdateResponse.
    """
    manager = MemoryManager()
    
    # Get existing incident
    incident = manager.get_incident(incident_id)
    if not incident:
        _logger.warning(f"Incident {incident_id} not found")
        raise HTTPException(status_code=404, detail="Incident not found")
    
    old_status = incident["payload"].get("status", "pending")
    new_status = request.status
    
    # Validate transition
    if not is_valid_transition(old_status, new_status):
        allowed = ALLOWED_STATUS_TRANSITIONS.get(old_status, [])
        _logger.warning(f"Invalid transition {old_status} -> {new_status}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition from '{old_status}' to '{new_status}'. Allowed: {allowed}",
        )
    
    # Update status
    success = manager.update_incident_payload(incident_id, {"status": new_status})
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update status")
    
    _logger.info(f"Updated incident {incident_id}: {old_status} -> {new_status}")
    
    return StatusUpdateResponse(
        incident_id=incident_id,
        old_status=old_status,
        new_status=new_status,
        message="Status updated successfully",
    )


@router.post("/incident/{incident_id}/reinforce", response_model=ReinforceResponse)
async def reinforce_incident(incident_id: str, request: ReinforceRequest):
    """Reinforce incident with new evidence.
    
    Args:
        incident_id: Incident UUID.
        request: New evidence data.
    
    Returns:
        ReinforceResponse with similarity and confidence update.
    """
    # Validate input
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="text cannot be empty")
    
    if request.source_type not in SUPPORTED_SOURCE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"source_type must be one of {SUPPORTED_SOURCE_TYPES}",
        )
    
    manager = MemoryManager()
    
    try:
        result = manager.reinforce(
            incident_id=incident_id,
            new_source_type=request.source_type,
            new_text=request.text,
        )
        
        _logger.info(f"Reinforcement for {incident_id}: accepted={result['accepted']}")
        
        return ReinforceResponse(**result)
    
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail="Incident not found")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        _logger.error(f"Reinforcement error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
