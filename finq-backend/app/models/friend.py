"""
Friend model for Nexus Community
"""
from sqlalchemy import Column, String, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from app.models.base import Base
import uuid
import enum


class FriendStatus(enum.Enum):
    """Friend request status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    BLOCKED = "blocked"


class Friend(Base):
    """Friend relationship model"""
    __tablename__ = "friends"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    friend_id = Column(String, nullable=False, index=True)
    status = Column(String, default=FriendStatus.PENDING.value)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "friend_id": self.friend_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

