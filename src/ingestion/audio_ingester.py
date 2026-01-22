"""Audio ingester for RESPOND incident reinforcement.

Phase 13.2: Audio ingestion pipeline.
Transcribes audio and reinforces existing incidents with the transcript.
"""

from pathlib import Path

from src.audio import transcribe_audio
from src.memory.memory_manager import MemoryManager
from src.utils.logger import get_logger

_logger = get_logger("ingestion.audio")

# Supported audio extensions
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".webm"}


class AudioIngester:
    """Ingests audio as evidence for existing incidents.
    
    Workflow:
    1. Validate input (incident_id, audio_path)
    2. Transcribe audio using Whisper
    3. Reinforce incident with transcript using MemoryManager
    4. Return reinforcement result
    
    Note: This does NOT create new incidents. It reinforces existing ones.
    """

    def __init__(self):
        self._memory_manager = MemoryManager()

    def ingest(self, data: dict) -> dict:
        """Ingest audio as evidence for an incident.
        
        Args:
            data: Audio data with required keys:
                - incident_id: UUID of existing incident to reinforce
                - audio_path: Path to audio file
                Optional:
                - source_type: Source type (default: "call")
                - zone_id: Zone identifier (not used in reinforcement)
        
        Returns:
            Dict with:
                - incident_id: Reinforced incident ID
                - transcript: Transcribed text
                - similarity: Similarity between transcript and incident
                - accepted: Whether reinforcement was accepted
                - new_confidence: Updated confidence score
        
        Raises:
            ValueError: If validation fails.
            FileNotFoundError: If audio file doesn't exist.
            RuntimeError: If transcription fails.
        """
        # Validate input
        self._validate(data)
        
        # Extract fields
        incident_id = data["incident_id"]
        audio_path = data["audio_path"]
        source_type = data.get("source_type", "call")
        
        _logger.info(f"Processing audio for incident {incident_id[:8]}...")
        
        # Step 1: Transcribe audio
        _logger.info(f"Transcribing audio: {audio_path}")
        transcript = transcribe_audio(audio_path)
        
        if not transcript or not transcript.strip():
            _logger.warning("Transcription produced empty text")
            return {
                "incident_id": incident_id,
                "transcript": "",
                "similarity": 0.0,
                "accepted": False,
                "new_confidence": None,
                "message": "Transcription produced no text",
            }
        
        _logger.info(f"Transcript: '{transcript[:100]}...'")
        
        # Step 2: Reinforce incident with transcript
        try:
            result = self._memory_manager.reinforce(
                incident_id=incident_id,
                new_source_type=source_type,
                new_text=transcript,
            )
        except ValueError as e:
            _logger.error(f"Reinforcement failed: {e}")
            raise
        
        _logger.info(
            f"Audio reinforcement: incident={incident_id[:8]}..., "
            f"similarity={result['similarity']:.3f}, "
            f"accepted={result['accepted']}, "
            f"new_confidence={result['new_confidence']:.3f}"
        )
        
        return {
            "incident_id": incident_id,
            "transcript": transcript,
            "similarity": result["similarity"],
            "accepted": result["accepted"],
            "old_confidence": result["old_confidence"],
            "new_confidence": result["new_confidence"],
            "reinforced_count": result["reinforced_count"],
        }

    def _validate(self, data: dict) -> None:
        """Validate audio ingestion data.
        
        Args:
            data: Input data to validate.
        
        Raises:
            ValueError: If validation fails.
            FileNotFoundError: If audio file doesn't exist.
        """
        # Required: incident_id
        incident_id = data.get("incident_id")
        if not incident_id or not incident_id.strip():
            raise ValueError("incident_id is required")
        
        # Required: audio_path
        audio_path = data.get("audio_path")
        if not audio_path:
            raise ValueError("audio_path is required")
        
        # Validate file exists
        path = Path(audio_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        if not path.is_file():
            raise ValueError(f"Path is not a file: {audio_path}")
        
        # Validate file extension
        ext = path.suffix.lower()
        if ext not in ALLOWED_AUDIO_EXTENSIONS:
            raise ValueError(
                f"Unsupported audio format '{ext}'. "
                f"Allowed: {sorted(ALLOWED_AUDIO_EXTENSIONS)}"
            )
