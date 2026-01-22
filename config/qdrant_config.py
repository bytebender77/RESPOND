"""
Qdrant Configuration

Collection names and constants for the RESPOND vector database.
"""

from enum import Enum

from config.settings import settings


# Collection names with configurable prefix
SITUATION_REPORTS = f"{settings.QDRANT_PREFIX}situation_reports"
DISASTER_EVENTS = f"{settings.QDRANT_PREFIX}disaster_events"
RESOURCE_DEPLOYMENTS = f"{settings.QDRANT_PREFIX}resource_deployments"
HISTORICAL_PATTERNS = f"{settings.QDRANT_PREFIX}historical_patterns"
INCIDENT_IMAGES = f"{settings.QDRANT_PREFIX}incident_images"  # Phase 12.2

# Supported source types for incident data
SUPPORTED_SOURCE_TYPES = ["social", "satellite", "call", "sensor", "report"]

# Image types for image incidents (Phase 12.2)
SUPPORTED_IMAGE_TYPES = ["photo", "satellite", "drone", "cctv", "screenshot"]

# Urgency levels for prioritization
SUPPORTED_URGENCY = ["critical", "high", "medium", "low"]

# Status tracking for incidents
SUPPORTED_STATUS = ["pending", "acknowledged", "resolved"]


class SourceType(str, Enum):
    """Enum for source types."""
    SOCIAL = "social"
    SATELLITE = "satellite"
    CALL = "call"
    SENSOR = "sensor"
    REPORT = "report"


class Urgency(str, Enum):
    """Enum for urgency levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Status(str, Enum):
    """Enum for incident status."""
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
