"""RESPOND API Main Application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from api.routes.setup import router as setup_router
from api.routes.ingest import router as ingest_router
from api.routes.search import router as search_router
from api.routes.memory import router as memory_router
from api.routes.recommend import router as recommend_router
from api.routes.images import router as images_router
from api.routes.audio import router as audio_router
from api.routes.deployments import router as deployments_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Real-time Emergency System for Priority-Ordered Neighborhood Dispatch",
    version="0.1.0",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(setup_router)
app.include_router(ingest_router)
app.include_router(search_router)
app.include_router(memory_router)
app.include_router(recommend_router)
app.include_router(images_router)
app.include_router(audio_router)
app.include_router(deployments_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}



