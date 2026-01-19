"""
RESPOND Configuration Settings

Centralized configuration using Pydantic Settings with environment variable support.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "RESPOND"
    ENV: str = "dev"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str | None = None
    QDRANT_PREFIX: str = "respond_"
    DEFAULT_VECTOR_SIZE: int = 384
    DEFAULT_DISTANCE: str = "Cosine"


# Singleton instance
settings = Settings()
