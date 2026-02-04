"""
User API Keys model for storing encrypted API keys
Supports BYOK (Bring Your Own Key) functionality
"""
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.models.base import Base
import uuid


class UserAPIKey(Base):
    """Store user's API keys securely (encrypted)"""
    __tablename__ = "user_api_keys"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)  # Firebase Auth UID
    
    # API Keys (encrypted)
    gemini_api_key_encrypted = Column(String, nullable=True)  # Encrypted Gemini key
    fred_api_key_encrypted = Column(String, nullable=True)  # Encrypted FRED key
    
    # Metadata
    gemini_key_last_validated = Column(DateTime(timezone=True), nullable=True)
    fred_key_last_validated = Column(DateTime(timezone=True), nullable=True)
    gemini_key_is_valid = Column(Boolean, default=False, nullable=True)
    fred_key_is_valid = Column(Boolean, default=False, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def to_dict(self, include_keys: bool = False):
        """Convert to dictionary (never include actual keys by default)"""
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "has_gemini_key": bool(self.gemini_api_key_encrypted),
            "has_fred_key": bool(self.fred_api_key_encrypted),
            "gemini_key_is_valid": self.gemini_key_is_valid,
            "fred_key_is_valid": self.fred_key_is_valid,
            "gemini_key_last_validated": self.gemini_key_last_validated.isoformat() if self.gemini_key_last_validated else None,
            "fred_key_last_validated": self.fred_key_last_validated.isoformat() if self.fred_key_last_validated else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        return data
