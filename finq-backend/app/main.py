"""
FinQ Backend API - Main Application
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import financial, chat, health, nexus, insights, media, websocket, data_pipeline, health_scores

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Backend API for FinQ financial analysis platform",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix=settings.api_prefix, tags=["health"])
app.include_router(financial.router, prefix=settings.api_prefix, tags=["financial"])
app.include_router(chat.router, prefix=settings.api_prefix, tags=["chat"])
app.include_router(nexus.router, prefix=settings.api_prefix, tags=["nexus"])
app.include_router(insights.router, prefix=settings.api_prefix, tags=["insights"])
app.include_router(media.router, prefix=settings.api_prefix, tags=["media"])
app.include_router(websocket.router, prefix=settings.api_prefix, tags=["websocket"])
app.include_router(data_pipeline.router, prefix=settings.api_prefix, tags=["data-pipeline"])
app.include_router(health_scores.router, prefix=settings.api_prefix, tags=["health-scores"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FinQ Backend API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )

