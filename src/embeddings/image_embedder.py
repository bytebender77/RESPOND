"""Image embedder using CLIP for RESPOND.

Phase 12.1: ImageEmbedder using OpenAI CLIP model.
CLIP produces 512-dimensional vectors suitable for image-text matching.
"""

import os
from pathlib import Path

from PIL import Image

from src.embeddings.base import BaseEmbedder
from src.utils.logger import get_logger

_logger = get_logger("embeddings.image")

# CLIP model configuration
CLIP_MODEL_NAME = "clip-ViT-B-32"
CLIP_VECTOR_SIZE = 512

# Singleton model instance
_clip_model = None
_fallback_mode = False


def _load_clip_model():
    """Load CLIP model with fallback."""
    global _clip_model, _fallback_mode
    
    if _clip_model is not None:
        return _clip_model
    
    try:
        from sentence_transformers import SentenceTransformer
        _clip_model = SentenceTransformer(CLIP_MODEL_NAME)
        _logger.info(f"Loaded CLIP model: {CLIP_MODEL_NAME}")
        _fallback_mode = False
    except Exception as e:
        _logger.warning(f"Failed to load CLIP model: {e}")
        _logger.warning("Image embedding not available")
        _fallback_mode = True
        _clip_model = None
    
    return _clip_model


class ImageEmbedder(BaseEmbedder):
    """Image embedder using OpenAI CLIP model.
    
    CLIP (Contrastive Language-Image Pre-training) creates embeddings
    that can match images with text in a shared vector space.
    
    Vector size: 512 dimensions
    """

    @property
    def name(self) -> str:
        """Embedder identifier."""
        return CLIP_MODEL_NAME

    @property
    def vector_size(self) -> int:
        """Output vector dimension for CLIP."""
        return CLIP_VECTOR_SIZE

    def embed_text(self, text: str) -> list[float]:
        """Generate CLIP text embedding.
        
        CLIP can embed both text and images in the same vector space,
        allowing text-to-image similarity search.
        
        Args:
            text: Input text to embed.
        
        Returns:
            Embedding vector as list of floats (512 dims).
        
        Raises:
            ValueError: If text is empty.
            RuntimeError: If CLIP model not available.
        """
        self._validate_text(text)
        
        model = _load_clip_model()
        
        if _fallback_mode or model is None:
            raise RuntimeError("CLIP model not available for text embedding")
        
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_image(self, image_path: str) -> list[float]:
        """Generate CLIP image embedding.
        
        Args:
            image_path: Path to image file (jpg, png, etc).
        
        Returns:
            Embedding vector as list of floats (512 dims).
        
        Raises:
            FileNotFoundError: If image file doesn't exist.
            ValueError: If image cannot be loaded.
            RuntimeError: If CLIP model not available.
        """
        # Validate file existence
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {image_path}")
        
        # Load CLIP model
        model = _load_clip_model()
        
        if _fallback_mode or model is None:
            raise RuntimeError("CLIP model not available for image embedding")
        
        try:
            # Load image using PIL
            image = Image.open(image_path)
            
            # Convert to RGB if needed (e.g., for PNG with alpha)
            if image.mode != "RGB":
                image = image.convert("RGB")
            
            _logger.debug(f"Loaded image: {image_path} ({image.size})")
            
            # Generate embedding
            embedding = model.encode(image, convert_to_numpy=True)
            
            _logger.info(f"Embedded image: {path.name} -> {len(embedding)} dims")
            return embedding.tolist()
            
        except Exception as e:
            _logger.error(f"Failed to embed image {image_path}: {e}")
            raise ValueError(f"Could not process image: {e}")

    def _validate_image_path(self, image_path: str) -> None:
        """Validate image path.
        
        Args:
            image_path: Path to validate.
        
        Raises:
            FileNotFoundError: If file doesn't exist.
            ValueError: If not a file.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        if not os.path.isfile(image_path):
            raise ValueError(f"Not a file: {image_path}")
