"""
User Profile model for storing user preferences and profile information
"""
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.models.base import Base
import uuid


class UserProfile(Base):
    """User profile and preferences"""
    __tablename__ = "user_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, unique=True, index=True)  # Firebase Auth UID
    
    # Profile information
    display_name = Column(String, nullable=True)  # Alias/display name (can override Firebase name)
    firebase_display_name = Column(String, nullable=True)  # Original display name from Firebase Auth
    profile_picture_url = Column(String, nullable=True)  # Custom profile picture URL (can override Firebase photo)
    firebase_photo_url = Column(String, nullable=True)  # Original photo URL from Firebase Auth
    
    # Preferences
    use_alias_as_display = Column(Boolean, default=False)  # Use alias instead of real name
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "display_name": self.display_name,
            "firebase_display_name": self.firebase_display_name,
            "profile_picture_url": self.profile_picture_url,
            "firebase_photo_url": self.firebase_photo_url,
            "use_alias_as_display": self.use_alias_as_display,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

