"""
Pydantic schemas for insight sharing endpoints
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class InsightShareRequest(BaseModel):
    """Schema for sharing an insight"""
    insight_id: str = Field(..., description="ID of insight to share")
    caption: Optional[str] = Field(None, description="Optional caption for the post")
    media_urls: Optional[List[str]] = Field(None, description="Media URLs (charts, images)")
    media_type: Optional[str] = Field(None, description="Type of media")
    tags: Optional[List[str]] = Field(None, description="Tags for the post")


class InsightShareResponse(BaseModel):
    """Schema for insight share response"""
    post_id: str
    insight_id: str
    message: str


class InsightListResponse(BaseModel):
    """Schema for list of insights"""
    insights: List[dict]
    count: int
    limit: int
    offset: int

