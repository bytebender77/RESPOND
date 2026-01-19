"""Base embedder interface for RESPOND."""

from abc import ABC, abstractmethod

from config.settings import settings


class BaseEmbedder(ABC):
    """Abstract base class for all embedding backends."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this embedder."""
        pass

    @property
    def vector_size(self) -> int:
        """Dimension of output vectors."""
        return settings.DEFAULT_VECTOR_SIZE

    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """Generate embedding for text input.
        
        Args:
            text: Input text to embed.
        
        Returns:
            Embedding vector as list of floats.
        
        Raises:
            ValueError: If text is empty.
        """
        pass

    def embed_image(self, image_path: str) -> list[float]:
        """Generate embedding for image input.
        
        Args:
            image_path: Path to image file.
        
        Returns:
            Embedding vector as list of floats.
        
        Raises:
            NotImplementedError: If not supported by this embedder.
        """
        raise NotImplementedError(f"{self.name} does not support image embedding")

    def embed_audio(self, audio_path: str) -> list[float]:
        """Generate embedding for audio input.
        
        Args:
            audio_path: Path to audio file.
        
        Returns:
            Embedding vector as list of floats.
        
        Raises:
            NotImplementedError: If not supported by this embedder.
        """
        raise NotImplementedError(f"{self.name} does not support audio embedding")

    def _validate_text(self, text: str) -> None:
        """Validate text input.
        
        Raises:
            ValueError: If text is empty or whitespace only.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
