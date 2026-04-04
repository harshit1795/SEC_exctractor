"""
Pydantic schemas for chat endpoints
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """Request schema for chat analysis"""
    prompt: str = Field(..., description="User's question or prompt")
    context_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Context data including selected tickers, metrics, etc."
    )
    session_id: Optional[str] = Field(None, description="Chat session ID for history")
    agentic_mode: bool = Field(False, description="Whether to use the autonomous tool-calling agent (True) or standard LLM (False)")


class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime
    metadata_json: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class ChatSessionResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    context_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class ChatSessionDetailResponse(ChatSessionResponse):
    messages: List[ChatMessageResponse] = []


class ChatResponse(BaseModel):
    """Response schema for chat analysis"""
    response: str
    insight_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatHistoryResponse(BaseModel):
    """Response schema for chat history"""
    user_id: str
    insights: List[Dict[str, Any]]
    count: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
