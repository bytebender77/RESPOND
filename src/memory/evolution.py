"""Status evolution rules for RESPOND incidents."""

# Allowed status transitions
ALLOWED_STATUS_TRANSITIONS = {
    "pending": ["acknowledged"],
    "acknowledged": ["resolved"],
    "resolved": ["resolved"],  # Terminal state
}


def is_valid_transition(old: str, new: str) -> bool:
    """Check if status transition is valid.
    
    Args:
        old: Current status.
        new: Target status.
    
    Returns:
        True if transition is allowed.
    """
    allowed = ALLOWED_STATUS_TRANSITIONS.get(old, [])
    return new in allowed
