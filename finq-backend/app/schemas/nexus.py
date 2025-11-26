"""
Pydantic schemas for Nexus Community endpoints
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ==================== POSTS ====================

class PostCreate(BaseModel):
    """Schema for creating a post"""
    content: str = Field(..., description="Post content")
    media_urls: Optional[List[str]] = Field(None, description="List of media URLs")
    media_type: Optional[str] = Field(None, description="Type of media (image, chart, video)")
    is_shared_insight: Optional[bool] = Field(False, description="Whether this is a shared insight")
    insight_id: Optional[str] = Field(None, description="ID of shared insight")
    tags: Optional[List[str]] = Field(None, description="List of tags")


class PostResponse(BaseModel):
    """Schema for post response"""
    id: str
    author_id: str
    content: str
    media_urls: List[str]
    media_type: Optional[str]
    likes_count: int
    comments_count: int
    shares_count: int
    is_shared_insight: bool
    insight_id: Optional[str]
    tags: List[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    liked: Optional[bool] = False  # Whether current user liked this
    comments: Optional[List[Dict[str, Any]]] = []


class PostListResponse(BaseModel):
    """Schema for list of posts"""
    posts: List[PostResponse]
    count: int
    limit: int
    offset: int


# ==================== COMMENTS ====================

class CommentCreate(BaseModel):
    """Schema for creating a comment"""
    content: str = Field(..., description="Comment content")


class CommentResponse(BaseModel):
    """Schema for comment response"""
    id: str
    post_id: str
    user_id: str
    content: str
    created_at: Optional[str]
    updated_at: Optional[str]


# ==================== FRIENDS ====================

class FriendRequest(BaseModel):
    """Schema for friend request"""
    friend_id: str = Field(..., description="ID of user to friend")


class FriendResponse(BaseModel):
    """Schema for friend response"""
    id: str
    user_id: str
    friend_id: str
    status: str
    created_at: Optional[str]
    updated_at: Optional[str]


class FriendListResponse(BaseModel):
    """Schema for list of friends"""
    friends: List[FriendResponse]
    count: int

