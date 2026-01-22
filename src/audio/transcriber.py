"""Audio transcription for RESPOND using OpenAI Whisper.

Phase 13.1: Audio transcription support.
Converts audio files to text using the Whisper speech-to-text model.
"""

import os
from pathlib import Path

from src.utils.logger import get_logger

_logger = get_logger("audio.transcriber")

# Whisper model configuration
# Options: "tiny", "base", "small", "medium", "large"
# Smaller models are faster but less accurate
DEFAULT_WHISPER_MODEL = "base"

# Supported audio extensions
SUPPORTED_AUDIO_FORMATS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".webm"}

# Singleton model instance
_whisper_model = None


def _load_whisper_model(model_name: str = DEFAULT_WHISPER_MODEL):
    """Load Whisper model with lazy initialization.
    
    Args:
        model_name: Whisper model size to load.
    
    Returns:
        Loaded whisper model.
    
    Raises:
        RuntimeError: If whisper package is not installed.
    """
    global _whisper_model
    
    if _whisper_model is not None:
        return _whisper_model
    
    try:
        import whisper
        _logger.info(f"Loading Whisper model: {model_name}")
        _whisper_model = whisper.load_model(model_name)
        _logger.info(f"Loaded Whisper model: {model_name}")
        return _whisper_model
    except ImportError:
        raise RuntimeError(
            "Whisper is not installed. Install with: pip install openai-whisper"
        )
    except Exception as e:
        _logger.error(f"Failed to load Whisper model: {e}")
        raise RuntimeError(f"Failed to load Whisper model: {e}")


def transcribe_audio(
    audio_path: str,
    model_name: str = DEFAULT_WHISPER_MODEL,
    language: str = None,
) -> str:
    """Transcribe audio file to text using Whisper.
    
    Args:
        audio_path: Path to audio file.
        model_name: Whisper model to use (tiny, base, small, medium, large).
        language: Optional language code (e.g., "en", "es"). Auto-detected if None.
    
    Returns:
        Transcribed text.
    
    Raises:
        FileNotFoundError: If audio file doesn't exist.
        ValueError: If file format is not supported.
        RuntimeError: If Whisper is not available or transcription fails.
    """
    # Validate file exists
    path = Path(audio_path)
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {audio_path}")
    
    # Validate file extension
    ext = path.suffix.lower()
    if ext not in SUPPORTED_AUDIO_FORMATS:
        raise ValueError(
            f"Unsupported audio format '{ext}'. "
            f"Supported: {sorted(SUPPORTED_AUDIO_FORMATS)}"
        )
    
    _logger.info(f"Transcribing audio: {audio_path}")
    
    # Load model
    model = _load_whisper_model(model_name)
    
    # Transcribe
    try:
        options = {}
        if language:
            options["language"] = language
        
        result = model.transcribe(str(audio_path), **options)
        transcript = result.get("text", "").strip()
        
        _logger.info(
            f"Transcription complete: {len(transcript)} chars, "
            f"detected_language={result.get('language', 'unknown')}"
        )
        
        return transcript
        
    except Exception as e:
        _logger.error(f"Transcription failed: {e}")
        raise RuntimeError(f"Transcription failed: {e}")


def get_audio_duration(audio_path: str) -> float:
    """Get duration of audio file in seconds.
    
    Args:
        audio_path: Path to audio file.
    
    Returns:
        Duration in seconds.
    
    Note:
        Requires ffprobe or similar. Falls back to 0.0 if unavailable.
    """
    try:
        import subprocess
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet", "-show_entries",
                "format=duration", "-of", "csv=p=0", str(audio_path)
            ],
            capture_output=True,
            text=True,
        )
        return float(result.stdout.strip())
    except Exception:
        _logger.debug("Could not determine audio duration")
        return 0.0
