"""Filter builders for Qdrant search in RESPOND."""

from datetime import datetime, timezone, timedelta

from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue,
    Range,
    GeoBoundingBox,
    GeoRadius,
    GeoPoint,
)


def build_status_filter(status: str | None) -> FieldCondition | None:
    """Build filter for status field.
    
    Args:
        status: Status value to filter on.
    
    Returns:
        FieldCondition or None if status is None.
    """
    if status is None:
        return None
    return FieldCondition(
        key="status",
        match=MatchValue(value=status),
    )


def build_urgency_filter(urgency: str | None) -> FieldCondition | None:
    """Build filter for urgency field.
    
    Args:
        urgency: Urgency value to filter on.
    
    Returns:
        FieldCondition or None if urgency is None.
    """
    if urgency is None:
        return None
    return FieldCondition(
        key="urgency",
        match=MatchValue(value=urgency),
    )


def build_zone_filter(zone_id: str | None) -> FieldCondition | None:
    """Build filter for zone_id field.
    
    Args:
        zone_id: Zone ID to filter on.
    
    Returns:
        FieldCondition or None if zone_id is None.
    """
    if zone_id is None:
        return None
    return FieldCondition(
        key="zone_id",
        match=MatchValue(value=zone_id),
    )


def build_time_filter(last_hours: int | None) -> FieldCondition | None:
    """Build filter for timestamp_unix within last N hours.
    
    Args:
        last_hours: Number of hours to look back.
    
    Returns:
        FieldCondition or None if last_hours is None.
    """
    if last_hours is None:
        return None
    
    # Calculate cutoff as Unix epoch seconds
    now_unix = int(datetime.now(timezone.utc).timestamp())
    cutoff_unix = now_unix - (last_hours * 3600)
    
    return FieldCondition(
        key="timestamp_unix",
        range=Range(gte=cutoff_unix),
    )


def build_geo_filter(
    center: dict | None,
    radius_km: float | None,
) -> FieldCondition | None:
    """Build geo-radius filter for location field.
    
    Args:
        center: Dict with 'lat' and 'lon' keys.
        radius_km: Radius in kilometers.
    
    Returns:
        FieldCondition or None if center/radius is None.
    """
    if center is None or radius_km is None:
        return None
    
    return FieldCondition(
        key="location",
        geo_radius=GeoRadius(
            center=GeoPoint(
                lat=float(center["lat"]),
                lon=float(center["lon"]),
            ),
            radius=radius_km * 1000,  # Convert to meters
        ),
    )


def combine_filters(filters: list) -> Filter | None:
    """Combine multiple FieldConditions into a single Filter.
    
    Args:
        filters: List of FieldConditions (may contain None values).
    
    Returns:
        Combined Filter or None if no valid filters.
    """
    # Remove None values
    valid_filters = [f for f in filters if f is not None]
    
    if not valid_filters:
        return None
    
    return Filter(must=valid_filters)
