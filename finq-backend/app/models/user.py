"""
User model for authentication and user management
PostgreSQL-based user system (no Firebase dependency)
"""
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.models.base import Base
import uuid
import hashlib


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)  # Hashed password
    
    # Profile information
    display_name = Column(String, nullable=True)  # User's display name
    profile_picture_url = Column(String, nullable=True)  # Profile picture URL
    
    # Preferences
    use_alias_as_display = Column(Boolean, default=False)  # Use alias instead of real name
    alias_name = Column(String, nullable=True)  # Optional alias name
    
    # Authentication
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Email verification
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def to_dict(self, include_sensitive: bool = False):
        """Convert user to dictionary"""
        data = {
            "id": self.id,
            "email": self.email,
            "display_name": self.display_name,
            "profile_picture_url": self.profile_picture_url,
            "alias_name": self.alias_name,
            "use_alias_as_display": self.use_alias_as_display,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_sensitive:
            data["is_active"] = self.is_active
            data["is_verified"] = self.is_verified
            data["last_login"] = self.last_login.isoformat() if self.last_login else None
        return data
    
    def get_effective_display_name(self) -> str:
        """Get the display name to show (alias if enabled, otherwise display_name, otherwise email)"""
        if self.use_alias_as_display and self.alias_name:
            return self.alias_name
        return self.display_name or self.email.split('@')[0] if self.email else 'User'
    
    def get_effective_profile_picture(self) -> str:
        """Get the profile picture URL or generate one"""
        if self.profile_picture_url:
            return self.profile_picture_url
        display_name = self.get_effective_display_name()
        return f"https://ui-avatars.com/api/?name={display_name.replace(' ', '+')}"

