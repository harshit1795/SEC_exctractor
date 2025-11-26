"""
Insight model for storing chat analysis results
"""
from sqlalchemy import Column, String, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from app.models.base import Base
import uuid


class Insight(Base):
    """
    Stores AI-generated financial insights from chat sessions.
    These can be shared to Nexus Community.
    """
    __tablename__ = "insights"
    
    # Use String for UUID to support both SQLite and PostgreSQL
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    chat_session_id = Column(String, nullable=True, index=True)
    
    # Content
    content = Column(JSON, nullable=False)  # Full chat context (prompt, response, context_data)
    summary = Column(String, nullable=True)  # Human-readable summary
    
    # Metadata
    tickers = Column(JSON, nullable=True)  # List of tickers analyzed
    media_urls = Column(JSON, nullable=True)  # Generated charts/images URLs
    tags = Column(JSON, nullable=True)  # Tags for categorization
    
    # Sharing
    shared = Column(Boolean, default=False, nullable=False)
    shared_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Insight(id={self.id}, user_id={self.user_id}, tickers={self.tickers})>"


