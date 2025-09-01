from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime

@dataclass
class UserProfile:
    uid: str
    display_name: str = ""
    bio: str = ""
    location: str = ""
    website: str = ""
    interests: List[str] = field(default_factory=list)
    expertise: List[str] = field(default_factory=list)
    profile_picture_url: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)

@dataclass
class UserConnections:
    uid: str
    friends: List[str] = field(default_factory=list)
    followers: List[str] = field(default_factory=list)
    following: List[str] = field(default_factory=list)
    requests: List[str] = field(default_factory=list)
    blocked: List[str] = field(default_factory=list)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Post:
    id: str
    author_id: str
    content: str
    post_type: str = "general"
    ticker: str = ""
    analysis_type: str = ""
    data_context: Dict[str, Any] = field(default_factory=dict)
    finq_modules_used: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    likes: List[str] = field(default_factory=list)
    visibility: str = "public"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Comment:
    id: str
    post_id: str
    author_id: str
    text: str
    likes: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Message:
    id: str
    from_user: str
    to_user: str
    text: str
    media_url: str = ""
    read: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
