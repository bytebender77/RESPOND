"""Text embedder using sentence-transformers for RESPOND."""

import hashlib

from config.settings import settings
from src.embeddings.base import BaseEmbedder
from src.utils.logger import get_logger

_logger = get_logger("embeddings.text")

# Singleton model instance
_model = None
_fallback_mode = False


def _load_model():
    """Load sentence-transformers model with fallback."""
    global _model, _fallback_mode
    
    if _model is not None:
        return _model
    
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        _logger.info("Loaded sentence-transformers model: all-MiniLM-L6-v2")
        _fallback_mode = False
    except Exception as e:
        _logger.warning(f"Failed to load sentence-transformers: {e}")
        _logger.warning("Using fallback hash-based embedding mode")
        _fallback_mode = True
        _model = None
    
    return _model


def _hash_to_vector(text: str, size: int) -> list[float]:
    """Generate deterministic pseudo-vector from text hash.
    
    Args:
        text: Input text.
        size: Target vector dimension.
    
    Returns:
        List of floats in range [0, 1].
    """
    # Generate hash and expand to required size
    result = []
    counter = 0
    
    while len(result) < size:
        hash_input = f"{text}:{counter}".encode()
        hash_bytes = hashlib.sha256(hash_input).digest()
        # Convert each byte to float in [0, 1]
        for b in hash_bytes:
            if len(result) >= size:
                break
            result.append(b / 255.0)
        counter += 1
    
    return result[:size]


class TextEmbedder(BaseEmbedder):
    """Text embedder using sentence-transformers."""

    @property
    def name(self) -> str:
        """Embedder identifier."""
        return "all-MiniLM-L6-v2"

    @property
    def vector_size(self) -> int:
        """Output vector dimension."""
        return settings.DEFAULT_VECTOR_SIZE

    def embed_text(self, text: str) -> list[float]:
        """Generate embedding for text.
        
        Args:
            text: Input text to embed.
        
        Returns:
            Embedding vector as list of floats.
        
        Raises:
            ValueError: If text is empty.
        """
        self._validate_text(text)
        
        model = _load_model()
        
        if _fallback_mode or model is None:
            _logger.debug("Using fallback hash embedding")
            return _hash_to_vector(text, self.vector_size)
        
        # Generate embedding using sentence-transformers
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
