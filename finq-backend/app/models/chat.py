from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class ChatSession(Base):
    """
    Model representing a distinct chat session.
    """
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=False)
    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Store any context associated with the session (e.g., attached tickers)
    context_data = Column(JSON, default=dict)

    # Relationships
    messages = relationship(
        "ChatMessage", 
        back_populates="session", 
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at"
    )


class ChatMessage(Base):
    """
    Model representing an individual message within a chat session.
    Role can be 'user', 'assistant', or 'system/tool'.
    """
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String, nullable=False)  # 'user', 'model', 'function'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Optional field to store function calling details or raw tool output metadata
    metadata_json = Column(JSON, default=dict)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")
