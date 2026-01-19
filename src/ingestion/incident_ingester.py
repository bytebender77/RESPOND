"""Incident ingester for RESPOND."""

from datetime import datetime, timezone

from config.qdrant_config import (
    SITUATION_REPORTS,
    SUPPORTED_SOURCE_TYPES,
    SUPPORTED_URGENCY,
    SUPPORTED_STATUS,
)
from src.ingestion.base_ingester import BaseIngester
from src.embeddings.text_embedder import TextEmbedder
from src.qdrant.indexer import upsert_point
from src.utils.ids import generate_uuid
from src.utils.time_utils import utc_now_iso, parse_iso_datetime
from src.utils.geo_utils import is_valid_lat_lon
from src.utils.logger import get_logger

_logger = get_logger("ingestion.incident")


def _iso_to_unix(iso_str: str) -> int:
    """Convert ISO timestamp to Unix epoch seconds."""
    dt = parse_iso_datetime(iso_str)
    return int(dt.timestamp())


class IncidentIngester(BaseIngester):
    """Ingests incident reports into Qdrant SITUATION_REPORTS collection."""

    def __init__(self):
        self._embedder = TextEmbedder()

    @property
    def name(self) -> str:
        """Ingester identifier."""
        return "incident_ingester"

    def ingest(self, data: dict) -> str:
        """Ingest an incident report.
        
        Args:
            data: Incident data with required keys: text, source_type.
        
        Returns:
            Inserted incident_id.
        
        Raises:
            ValueError: If validation fails.
        """
        # Validate required fields
        self._validate(data)
        
        # Extract and normalize fields
        text = data["text"]
        source_type = data["source_type"]
        now = utc_now_iso()
        now_unix = int(datetime.now(timezone.utc).timestamp())
        
        timestamp = data.get("timestamp", now)
        timestamp_unix = _iso_to_unix(timestamp) if data.get("timestamp") else now_unix
        
        urgency = data.get("urgency", "medium")
        status = data.get("status", "pending")
        zone_id = data.get("zone_id", "unknown")
        confidence_score = data.get("confidence_score", 0.5)
        location = data.get("location")
        
        # Generate embedding
        vector = self._embedder.embed_text(text)
        
        # Build payload
        payload = {
            "text": text,
            "source_type": source_type,
            "timestamp": timestamp,
            "timestamp_unix": timestamp_unix,
            "urgency": urgency,
            "status": status,
            "zone_id": zone_id,
            "confidence_score": float(confidence_score),
            "created_at": now,
            "updated_at": now,
        }
        
        # Add location if provided
        if location:
            payload["location"] = {
                "lat": float(location["lat"]),
                "lon": float(location["lon"]),
            }
        
        # Generate ID and upsert
        incident_id = generate_uuid()
        upsert_point(
            collection=SITUATION_REPORTS,
            point_id=incident_id,
            vector=vector,
            payload=payload,
        )
        
        _logger.info(f"Ingested incident {incident_id} from {source_type}")
        return incident_id

    def _validate(self, data: dict) -> None:
        """Validate incident data.
        
        Raises:
            ValueError: If validation fails.
        """
        # Required: text
        text = data.get("text", "")
        if not text or not text.strip():
            raise ValueError("text is required and cannot be empty")
        
        # Required: source_type
        source_type = data.get("source_type")
        if not source_type:
            raise ValueError("source_type is required")
        if source_type not in SUPPORTED_SOURCE_TYPES:
            raise ValueError(
                f"source_type must be one of {SUPPORTED_SOURCE_TYPES}, got '{source_type}'"
            )
        
        # Optional: urgency
        urgency = data.get("urgency", "medium")
        if urgency not in SUPPORTED_URGENCY:
            raise ValueError(
                f"urgency must be one of {SUPPORTED_URGENCY}, got '{urgency}'"
            )
        
        # Optional: status
        status = data.get("status", "pending")
        if status not in SUPPORTED_STATUS:
            raise ValueError(
                f"status must be one of {SUPPORTED_STATUS}, got '{status}'"
            )
        
        # Optional: location validation
        location = data.get("location")
        if location:
            lat = location.get("lat")
            lon = location.get("lon")
            if lat is None or lon is None:
                raise ValueError("location must have 'lat' and 'lon' keys")
            if not is_valid_lat_lon(lat, lon):
                raise ValueError(f"Invalid coordinates: lat={lat}, lon={lon}")
