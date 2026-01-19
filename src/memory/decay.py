"""Time-decay utilities for RESPOND incident ranking."""

from datetime import datetime, timezone

from src.utils.logger import get_logger

_logger = get_logger("memory.decay")


def compute_decay_factor(age_seconds: int) -> float:
    """Compute decay factor based on age.
    
    Args:
        age_seconds: Age of incident in seconds.
    
    Returns:
        Decay factor (0.0 to 1.0).
    """
    if age_seconds <= 3600:  # <= 1 hour
        return 1.0
    elif age_seconds <= 21600:  # <= 6 hours
        return 0.8
    elif age_seconds <= 86400:  # <= 24 hours
        return 0.5
    else:
        return 0.2


def apply_decay(similarity_score: float, timestamp_unix: int | None) -> dict:
    """Apply time-based decay to similarity score.
    
    Args:
        similarity_score: Original Qdrant similarity score.
        timestamp_unix: Unix epoch timestamp of incident.
    
    Returns:
        Dict with final_score, decay_factor, and age_seconds.
    """
    # Handle missing timestamp
    if timestamp_unix is None:
        return {
            "final_score": similarity_score,
            "decay_factor": 1.0,
            "age_seconds": 0,
        }
    
    # Compute age
    now_unix = int(datetime.now(timezone.utc).timestamp())
    age_seconds = max(0, now_unix - timestamp_unix)
    
    # Compute decay
    decay_factor = compute_decay_factor(age_seconds)
    final_score = similarity_score * decay_factor
    
    return {
        "final_score": final_score,
        "decay_factor": decay_factor,
        "age_seconds": age_seconds,
    }
