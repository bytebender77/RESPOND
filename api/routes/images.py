"""Image routes for RESPOND API.

Phase 12.4: Image upload and ingestion endpoints.
"""

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from config.qdrant_config import SUPPORTED_IMAGE_TYPES
from src.ingestion import ImageIngester
from src.utils.logger import get_logger

router = APIRouter(prefix="/ingest", tags=["images"])
_logger = get_logger("api.images")

# Upload directory
UPLOAD_DIR = Path("uploads/images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}


class ImageIngestResponse(BaseModel):
    """Response model for image ingestion."""
    incident_id: str
    image_point_id: str
    message: str
    image_path: str | None = None


@router.post(
    "/incident/{incident_id}/image",
    response_model=ImageIngestResponse,
    summary="Upload and ingest an incident image",
)
async def upload_incident_image(
    incident_id: str,
    file: UploadFile = File(..., description="Image file to upload"),
    image_type: str = Form(default="photo", description="Type of image"),
    zone_id: str = Form(default=None, description="Optional zone ID"),
):
    """Upload an image and ingest it into Qdrant.
    
    Args:
        incident_id: UUID of the parent incident.
        file: Image file (multipart/form-data).
        image_type: Type of image (photo, satellite, drone, cctv, screenshot).
        zone_id: Optional zone identifier.
    
    Returns:
        ImageIngestResponse with incident_id, image_point_id, and message.
    
    Raises:
        400: Invalid file type or image_type.
        500: Server error during processing.
    """
    try:
        # Validate incident_id
        if not incident_id or not incident_id.strip():
            raise HTTPException(status_code=400, detail="incident_id is required")
        
        # Validate image_type
        if image_type not in SUPPORTED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"image_type must be one of {SUPPORTED_IMAGE_TYPES}",
            )
        
        # Validate file extension
        original_filename = file.filename or "image.jpg"
        ext = Path(original_filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{ext}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
            )
        
        # Generate unique filename
        unique_filename = f"{incident_id[:8]}_{uuid.uuid4().hex[:8]}{ext}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save uploaded file
        _logger.info(f"Saving uploaded file: {file_path}")
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Prepare ingestion data
        data = {
            "incident_id": incident_id,
            "image_path": str(file_path.absolute()),
            "image_type": image_type,
        }
        if zone_id:
            data["zone_id"] = zone_id
        
        # Ingest image
        ingester = ImageIngester()
        image_point_id = ingester.ingest(data)
        
        _logger.info(
            f"API ingested image {image_point_id[:8]}... "
            f"for incident {incident_id[:8]}..."
        )
        
        return ImageIngestResponse(
            incident_id=incident_id,
            image_point_id=image_point_id,
            message="Image uploaded and ingested successfully",
            image_path=str(file_path),
        )
    
    except HTTPException:
        raise
    except FileNotFoundError as e:
        _logger.error(f"File error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        _logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        _logger.error(f"Image ingest error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
