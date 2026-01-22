"""Image ingester for RESPOND incident images.

Phase 12.3: Image ingestion pipeline.
Stores image embeddings in respond_incident_images collection.
"""

import os
from datetime import datetime, timezone
from pathlib import Path

from config.qdrant_config import INCIDENT_IMAGES, SUPPORTED_IMAGE_TYPES
from src.embeddings.image_embedder import ImageEmbedder
from src.qdrant.indexer import upsert_point
from src.utils.ids import generate_uuid
from src.utils.time_utils import utc_now_iso
from src.utils.logger import get_logger

_logger = get_logger("ingestion.image")

# Supported image file extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}


class ImageIngester:
    """Ingests incident images into Qdrant INCIDENT_IMAGES collection.
    
    Workflow:
    1. Validate input (incident_id, image_path, image_type)
    2. Embed image using CLIP (512-dim vectors)
    3. Store in Qdrant with metadata
    4. Return image_point_id
    """

    def __init__(self):
        self._embedder = ImageEmbedder()

    def ingest(self, data: dict) -> str:
        """Ingest an incident image.
        
        Args:
            data: Image data with required keys:
                - incident_id: UUID of parent incident
                - image_path: Path to image file
                - image_type: Type of image (photo, satellite, drone, etc.)
                Optional:
                - zone_id: Zone identifier
        
        Returns:
            Inserted image_point_id (UUID).
        
        Raises:
            ValueError: If validation fails.
            FileNotFoundError: If image file doesn't exist.
        """
        # Validate input
        self._validate(data)
        
        # Extract fields
        incident_id = data["incident_id"]
        image_path = data["image_path"]
        image_type = data["image_type"]
        zone_id = data.get("zone_id")
        
        # Generate timestamps
        now = utc_now_iso()
        now_unix = int(datetime.now(timezone.utc).timestamp())
        
        # Embed image using CLIP
        _logger.info(f"Embedding image: {image_path}")
        vector = self._embedder.embed_image(image_path)
        
        # Build payload
        payload = {
            "incident_id": incident_id,
            "image_type": image_type,
            "image_path": str(image_path),
            "timestamp_unix": now_unix,
            "created_at": now,
        }
        
        # Add optional zone_id
        if zone_id:
            payload["zone_id"] = zone_id
        
        # Generate ID and upsert to Qdrant
        image_point_id = generate_uuid()
        upsert_point(
            collection=INCIDENT_IMAGES,
            point_id=image_point_id,
            vector=vector,
            payload=payload,
        )
        
        _logger.info(
            f"Ingested image {image_point_id[:8]}... "
            f"for incident {incident_id[:8]}... ({image_type})"
        )
        return image_point_id

    def _validate(self, data: dict) -> None:
        """Validate image ingestion data.
        
        Args:
            data: Input data to validate.
        
        Raises:
            ValueError: If validation fails.
            FileNotFoundError: If image file doesn't exist.
        """
        # Required: incident_id
        incident_id = data.get("incident_id")
        if not incident_id or not incident_id.strip():
            raise ValueError("incident_id is required")
        
        # Required: image_path
        image_path = data.get("image_path")
        if not image_path:
            raise ValueError("image_path is required")
        
        # Validate file exists
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        if not path.is_file():
            raise ValueError(f"Path is not a file: {image_path}")
        
        # Validate file extension
        ext = path.suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Unsupported image format '{ext}'. "
                f"Allowed: {sorted(ALLOWED_EXTENSIONS)}"
            )
        
        # Required: image_type
        image_type = data.get("image_type")
        if not image_type:
            raise ValueError("image_type is required")
        if image_type not in SUPPORTED_IMAGE_TYPES:
            raise ValueError(
                f"image_type must be one of {SUPPORTED_IMAGE_TYPES}, "
                f"got '{image_type}'"
            )
