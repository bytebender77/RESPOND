"""Request models for RESPOND API."""

from pydantic import BaseModel


class IncidentIngestRequest(BaseModel):
    """Request model for incident ingestion."""
    
    text: str
    source_type: str
    timestamp: str | None = None
    urgency: str = "medium"
    status: str = "pending"
    zone_id: str = "unknown"
    confidence_score: float = 0.5
    location: dict | None = None  # {"lat": float, "lon": float}


class IncidentSearchRequest(BaseModel):
    """Request model for incident search."""
    
    query: str
    limit: int = 10
    zone_id: str | None = None
    urgency: str | None = None
    status: str | None = None
    last_hours: int | None = None
    center: dict | None = None  # {"lat": float, "lon": float}
    radius_km: float | None = None
