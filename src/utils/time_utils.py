"""Time utilities for RESPOND."""

from datetime import datetime, timezone, timedelta


def utc_now_iso() -> str:
    """Get current UTC timestamp as ISO string with timezone."""
    return datetime.now(timezone.utc).isoformat()


def parse_iso_datetime(dt_str: str) -> datetime:
    """Parse ISO datetime string to datetime object.
    
    Args:
        dt_str: ISO timestamp (e.g., "2026-01-19T12:00:00Z" or "2026-01-19T12:00:00+00:00")
    
    Returns:
        Parsed datetime object with timezone info.
    """
    # Handle 'Z' suffix (Zulu time = UTC)
    if dt_str.endswith("Z"):
        dt_str = dt_str[:-1] + "+00:00"
    return datetime.fromisoformat(dt_str)


def hours_ago_iso(hours: int) -> str:
    """Get ISO timestamp for UTC time `hours` ago.
    
    Args:
        hours: Number of hours to subtract from current time.
    
    Returns:
        ISO formatted timestamp string.
    """
    dt = datetime.now(timezone.utc) - timedelta(hours=hours)
    return dt.isoformat()
