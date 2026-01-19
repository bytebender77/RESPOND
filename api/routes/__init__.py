"""RESPOND API Routes Package."""

from api.routes.setup import router as setup_router
from api.routes.ingest import router as ingest_router
from api.routes.search import router as search_router
from api.routes.memory import router as memory_router
from api.routes.recommend import router as recommend_router

__all__ = [
    "setup_router",
    "ingest_router",
    "search_router",
    "memory_router",
    "recommend_router",
]
