"""RESPOND Audio Package.

Phase 13.1: Audio transcription support using OpenAI Whisper.
"""

from src.audio.transcriber import transcribe_audio, get_audio_duration

__all__ = ["transcribe_audio", "get_audio_duration"]
