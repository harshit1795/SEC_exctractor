"""
Configuration management for FinQ Backend API
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "FinQ Backend API"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    api_prefix: str = Field(default="/api", env="API_PREFIX")
    
    # Database (default to SQLite for quick development)
    database_url: str = Field(
        default="sqlite:///./finq.db",
        env="DATABASE_URL"
    )
    
    # API Keys (optional for development, will error when actually used)
    gemini_api_key: str = Field(
        default="",
        env="GEMINI_API_KEY"
    )
    fred_api_key: str = Field(
        default="",
        env="FRED_API_KEY"
    )
    
    # Firebase
    firebase_credentials_json: str = Field(default="", env="FIREBASE_CREDENTIALS_JSON")
    firebase_credentials_path: str = Field(default="", env="FIREBASE_CREDENTIALS_PATH")
    
    # Encryption (for BYOK - Bring Your Own Key)
    encryption_key: str = Field(default="", env="ENCRYPTION_KEY")
    
    # CORS (comma-separated string, will be split)
    cors_origins: str = Field(
        default="http://localhost:8501,http://localhost:3000,http://localhost:8080",
        env="CORS_ORIGINS"
    )
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins as a list"""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
    # Cache
    cache_ttl: int = Field(default=300, env="CACHE_TTL")  # 5 minutes
    
    # Data Paths (relative to project root)
    data_dir: str = Field(default="../data", env="DATA_DIR")
    cik_map_path: str = Field(default="../secedgarticker.json", env="CIK_MAP_PATH")
    fundamentals_path: str = Field(default="../fundamentals_tall.parquet", env="FUNDAMENTALS_PATH")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

