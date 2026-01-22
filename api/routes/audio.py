"""Audio routes for RESPOND API.

Phase 13.3: Audio upload and transcription endpoints.
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from src.ingestion import AudioIngester
from src.utils.logger import get_logger

router = APIRouter(prefix="/memory", tags=["audio"])
_logger = get_logger("api.audio")

# Upload directory
UPLOAD_DIR = Path("uploads/audio")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed audio extensions
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".webm"}


class AudioReinforcementResponse(BaseModel):
    """Response model for audio reinforcement."""
    incident_id: str
    transcript: str
    similarity: float
    accepted: bool
    old_confidence: float | None = None
    new_confidence: float | None = None
    reinforced_count: int | None = None
    message: str
    audio_path: str | None = None


@router.post(
    "/incident/{incident_id}/reinforce_audio",
    response_model=AudioReinforcementResponse,
    summary="Reinforce an incident with audio evidence",
)
async def reinforce_with_audio(
    incident_id: str,
    file: UploadFile = File(..., description="Audio file to transcribe and use as evidence"),
    source_type: str = Form(default="call", description="Source type for the evidence"),
):
    """Upload audio, transcribe it, and reinforce an existing incident.
    
    Workflow:
    1. Save uploaded audio file
    2. Transcribe using Whisper
    3. Reinforce incident with transcript
    4. Return reinforcement result
    
    Args:
        incident_id: UUID of existing incident to reinforce.
        file: Audio file (multipart/form-data).
        source_type: Source type (default: "call").
    
    Returns:
        AudioReinforcementResponse with transcript and reinforcement details.
    
    Raises:
        400: Invalid file type or incident not found.
        500: Transcription or server error.
    """
    try:
        # Validate incident_id
        if not incident_id or not incident_id.strip():
            raise HTTPException(status_code=400, detail="incident_id is required")
        
        # Validate file extension
        original_filename = file.filename or "audio.wav"
        ext = Path(original_filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio format '{ext}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
            )
        
        # Generate unique filename
        unique_filename = f"{incident_id[:8]}_{uuid.uuid4().hex[:8]}{ext}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save uploaded file
        _logger.info(f"Saving audio file: {file_path}")
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Prepare ingestion data
        data = {
            "incident_id": incident_id,
            "audio_path": str(file_path.absolute()),
            "source_type": source_type,
        }
        
        # Run audio ingestion (transcribe + reinforce)
        ingester = AudioIngester()
        result = ingester.ingest(data)
        
        _logger.info(
            f"API audio reinforcement: incident={incident_id[:8]}..., "
            f"accepted={result.get('accepted', False)}"
        )
        
        return AudioReinforcementResponse(
            incident_id=result["incident_id"],
            transcript=result.get("transcript", ""),
            similarity=result.get("similarity", 0.0),
            accepted=result.get("accepted", False),
            old_confidence=result.get("old_confidence"),
            new_confidence=result.get("new_confidence"),
            reinforced_count=result.get("reinforced_count"),
            message="Audio processed and incident reinforced" if result.get("accepted") else "Audio processed but not similar enough",
            audio_path=str(file_path),
        )
    
    except HTTPException:
        raise
    except FileNotFoundError as e:
        _logger.error(f"File error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        _logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        _logger.error(f"Runtime error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        _logger.error(f"Audio reinforcement error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
