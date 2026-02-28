"""
Health check and diagnostic endpoints
"""
from fastapi import APIRouter
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "service": "FinQ Backend API"}


@router.get("/config")
async def config_check():
    """Check configuration status (without exposing sensitive data)"""
    config_status = {
        "database_configured": bool(settings.database_url),
        "gemini_api_key_configured": bool(settings.gemini_api_key and len(settings.gemini_api_key) > 0),
        "fred_api_key_configured": bool(settings.fred_api_key and len(settings.fred_api_key) > 0),
        "gemini_api_key_length": len(settings.gemini_api_key) if settings.gemini_api_key else 0,
        "fred_api_key_length": len(settings.fred_api_key) if settings.fred_api_key else 0,
    }
    
    # Check if keys look valid (start with expected patterns)
    if config_status["gemini_api_key_configured"]:
        key = settings.gemini_api_key
        config_status["gemini_api_key_valid_format"] = (
            len(key) > 20 and  # Google API keys are typically long
            (key.startswith("AIza") or "api" in key.lower() or len(key) > 30)
        )
    
    return config_status


@router.get("/cors")
async def cors_check():
    """Diagnostic endpoint to see exactly what Origins are configured on the server"""
    return {
        "raw_env_variable": settings.cors_origins,
        "parsed_origins": settings.get_cors_origins(),
        "host": settings.app_name
    }
