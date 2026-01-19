"""Response models for RESPOND API."""

from pydantic import BaseModel


class IngestResponse(BaseModel):
    """Response model for ingestion endpoints."""
    
    incident_id: str
    message: str


class SearchResultItem(BaseModel):
    """Single search result item with decay and evidence info."""
    
    id: str
    score: float
    payload: dict
    final_score: float
    decay_factor: float
    age_seconds: int
    evidence: dict


class SearchResponse(BaseModel):
    """Response model for search endpoints."""
    
    count: int
    results: list[SearchResultItem]
