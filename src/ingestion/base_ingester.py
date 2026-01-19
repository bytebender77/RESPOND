"""Base ingester interface for RESPOND."""

from abc import ABC, abstractmethod


class BaseIngester(ABC):
    """Abstract base class for all data ingesters."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this ingester."""
        pass

    @abstractmethod
    def ingest(self, data: dict) -> str:
        """Ingest data and return identifier.
        
        Args:
            data: Input data dictionary.
        
        Returns:
            Identifier of ingested record.
        """
        pass
