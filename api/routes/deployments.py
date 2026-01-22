"""Deployment routes for RESPOND API.

Phase 15.1: Resource deployment endpoints.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.resources import DeploymentManager, DEPLOYMENT_STATUSES
from src.utils.logger import get_logger

router = APIRouter(prefix="/deployments", tags=["deployments"])
_logger = get_logger("api.deployments")


class CreateDeploymentRequest(BaseModel):
    """Request model for creating a deployment."""
    action_type: str
    incident_ids: list[str]
    assigned_unit: str
    status: str = "assigned"
    zone_id: str | None = None
    notes: str | None = None


class CreateDeploymentResponse(BaseModel):
    """Response model for deployment creation."""
    deployment_id: str
    action_type: str
    assigned_unit: str
    status: str
    incident_count: int
    message: str


class UpdateStatusRequest(BaseModel):
    """Request model for status update."""
    status: str
    notes: str | None = None


class UpdateStatusResponse(BaseModel):
    """Response model for status update."""
    deployment_id: str
    old_status: str
    new_status: str
    message: str


class DeploymentResponse(BaseModel):
    """Response model for deployment details."""
    deployment_id: str
    action_type: str
    assigned_unit: str
    status: str
    incident_ids: list[str]
    zone_id: str | None = None
    created_at: str
    updated_at: str


@router.post("/create", response_model=CreateDeploymentResponse)
async def create_deployment(request: CreateDeploymentRequest):
    """Create a new resource deployment.
    
    Args:
        request: Deployment data.
    
    Returns:
        CreateDeploymentResponse with deployment_id.
    """
    try:
        manager = DeploymentManager()
        
        result = manager.create_deployment(
            action_type=request.action_type,
            incident_ids=request.incident_ids,
            assigned_unit=request.assigned_unit,
            status=request.status,
            zone_id=request.zone_id,
            notes=request.notes,
        )
        
        _logger.info(f"API created deployment {result['deployment_id'][:8]}...")
        
        return CreateDeploymentResponse(
            deployment_id=result["deployment_id"],
            action_type=result["action_type"],
            assigned_unit=result["assigned_unit"],
            status=result["status"],
            incident_count=result["incident_count"],
            message="Deployment created successfully",
        )
    
    except ValueError as e:
        _logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        _logger.error(f"Deployment creation error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/{deployment_id}/status", response_model=UpdateStatusResponse)
async def update_deployment_status(deployment_id: str, request: UpdateStatusRequest):
    """Update deployment status.
    
    Args:
        deployment_id: Deployment UUID.
        request: New status data.
    
    Returns:
        UpdateStatusResponse with old and new status.
    """
    try:
        # Validate status
        if request.status not in DEPLOYMENT_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"status must be one of {DEPLOYMENT_STATUSES}",
            )
        
        manager = DeploymentManager()
        
        result = manager.update_deployment_status(
            deployment_id=deployment_id,
            new_status=request.status,
            notes=request.notes,
        )
        
        _logger.info(
            f"API updated deployment {deployment_id[:8]}... "
            f"status: {result['old_status']} -> {result['new_status']}"
        )
        
        return UpdateStatusResponse(
            deployment_id=result["deployment_id"],
            old_status=result["old_status"],
            new_status=result["new_status"],
            message="Deployment status updated",
        )
    
    except ValueError as e:
        _logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        _logger.error(f"Status update error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(deployment_id: str):
    """Get deployment details.
    
    Args:
        deployment_id: Deployment UUID.
    
    Returns:
        DeploymentResponse with details.
    """
    try:
        manager = DeploymentManager()
        deployment = manager.get_deployment(deployment_id)
        
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")
        
        payload = deployment["payload"]
        
        return DeploymentResponse(
            deployment_id=deployment["id"],
            action_type=payload.get("action_type", ""),
            assigned_unit=payload.get("assigned_unit", ""),
            status=payload.get("status", ""),
            incident_ids=payload.get("incident_ids", []),
            zone_id=payload.get("zone_id"),
            created_at=payload.get("created_at", ""),
            updated_at=payload.get("updated_at", ""),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        _logger.error(f"Get deployment error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
