"""Geo utilities for RESPOND."""


def km_to_meters(km: float) -> float:
    """Convert kilometers to meters."""
    return km * 1000.0


def is_valid_lat_lon(lat: float, lon: float) -> bool:
    """Check if latitude and longitude are valid.
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
    
    Returns:
        True if coordinates are valid.
    """
    return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0


def normalize_location(lat: float, lon: float) -> dict:
    """Normalize location to a standard dict format.
    
    Args:
        lat: Latitude value.
        lon: Longitude value.
    
    Returns:
        Dict with 'lat' and 'lon' keys as floats.
    """
    return {"lat": float(lat), "lon": float(lon)}
