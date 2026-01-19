"""ID generation utilities for RESPOND."""

import uuid


def generate_uuid() -> str:
    """Generate a random UUID4 string."""
    return str(uuid.uuid4())
