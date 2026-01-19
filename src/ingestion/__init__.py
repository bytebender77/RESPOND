"""RESPOND Ingestion Package."""

from src.ingestion.base_ingester import BaseIngester
from src.ingestion.incident_ingester import IncidentIngester

__all__ = ["BaseIngester", "IncidentIngester"]
