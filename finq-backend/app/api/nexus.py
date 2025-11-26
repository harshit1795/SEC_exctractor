"""
Nexus Community API endpoints
Social features: posts, feed, friends, sharing
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.post import Post, PostLike, PostComment
from app.models.friend import Friend, FriendStatus
from app.models.insight import Insight
from app.api.websocket import broadcast_new_post
from app.schemas.nexus import (
    PostCreate, PostResponse, PostListResponse,
    FriendRequest, FriendResponse, FriendListResponse,
    CommentCreate, CommentResponse
)
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/nexus", tags=["nexus"])


# ==================== POSTS ====================

@router.post("/posts", response_model=PostResponse)
async def create_post(
    post_data: PostCreate,
    user_id: str = Query(default="anonymous", description="User ID"),  # TODO: Get from auth token
    db: Session = Depends(get_db)
):
    """
    Create a new post
    
    Args:
        post_data: Post content and metadata
        user_id: Current user ID (from auth)
        db: Database session
    
    Returns:
        Created post
    """
    try:
        post = Post(
            id=str(uuid.uuid4()),
            author_id=user_id,
            content=post_data.content,
            media_urls=post_data.media_urls or [],
            media_type=post_data.media_type,
            is_shared_insight=post_data.is_shared_insight or False,
            insight_id=post_data.insight_id,
            tags=post_data.tags or []
        )
        
        db.add(post)
        db.commit()
        db.refresh(post)
        
        # Broadcast new post via WebSocket
        try:
            await broadcast_new_post(post.to_dict())
        except Exception as e:
            logger.warning(f"Failed to broadcast new post: {e}")
        
        return PostResponse(**post.to_dict())
        
    except Exception as e:
        logger.error(f"Error creating post: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating post: {str(e)}"
        )


@router.get("/posts/feed", response_model=PostListResponse)
async def get_feed(
    user_id: str = Query(default="anonymous", description="User ID"),  # TODO: Get from auth token
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get feed of posts from friends
    
    Args:
        user_id: Current user ID
        limit: Maximum number of posts
        offset: Pagination offset
        db: Database session
    
    Returns:
        List of posts from friends
    """
    try:
        # Get list of friend IDs
        friends = db.query(Friend).filter(
            Friend.user_id == user_id,
            Friend.status == FriendStatus.ACCEPTED.value
        ).all()
        
        friend_ids = [f.friend_id for f in friends]
        friend_ids.append(user_id)  # Include own posts
        
        # Get posts from friends
        posts = db.query(Post).filter(
            Post.author_id.in_(friend_ids)
        ).order_by(
            Post.created_at.desc()
        ).limit(limit).offset(offset).all()
        
        # Get like status for each post
        post_responses = []
        for post in posts:
            post_dict = post.to_dict()
            # Check if user liked this post
            like = db.query(PostLike).filter(
                PostLike.post_id == post.id,
                PostLike.user_id == user_id
            ).first()
            post_dict["liked"] = like is not None
            
            # Get comments
            comments = db.query(PostComment).filter(
                PostComment.post_id == post.id
            ).order_by(PostComment.created_at.desc()).all()
            post_dict["comments"] = [c.to_dict() for c in comments]
            
            post_responses.append(post_dict)
        
        return PostListResponse(
            posts=post_responses,
            count=len(post_responses),
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        logger.error(f"Error getting feed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting feed: {str(e)}"
        )


@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    user_id: str = Query(default="anonymous", description="User ID"),  # TODO: Get from auth token
    db: Session = Depends(get_db)
):
    """
    Get a single post by ID
    
    Args:
        post_id: Post ID
        user_id: Current user ID
        db: Database session
    
    Returns:
        Post details
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post_dict = post.to_dict()
    
    # Check if user liked this post
    like = db.query(PostLike).filter(
        PostLike.post_id == post.id,
        PostLike.user_id == user_id
    ).first()
    post_dict["liked"] = like is not None
    
    # Get comments
    comments = db.query(PostComment).filter(
        PostComment.post_id == post.id
    ).order_by(PostComment.created_at.desc()).all()
    post_dict["comments"] = [c.to_dict() for c in comments]
    
    return PostResponse(**post_dict)


@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: str,
    user_id: str = Query(default="anonymous", description="User ID"),  # TODO: Get from auth token
    db: Session = Depends(get_db)
):
    """
    Like a post
    
    Args:
        post_id: Post ID
        user_id: Current user ID
        db: Database session
    
    Returns:
        Success message
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if already liked
    existing_like = db.query(PostLike).filter(
        PostLike.post_id == post_id,
        PostLike.user_id == user_id
    ).first()
    
    if existing_like:
        raise HTTPException(status_code=400, detail="Post already liked")
    
    # Create like
    like = PostLike(
        id=str(uuid.uuid4()),
        post_id=post_id,
        user_id=user_id
    )
    
    # Update post likes count
    post.likes_count += 1
    
    db.add(like)
    db.commit()
    
    return {"message": "Post liked", "likes_count": post.likes_count}


@router.delete("/posts/{post_id}/like")
async def unlike_post(
    post_id: str,
    user_id: str = Query(default="anonymous", description="User ID"),  # TODO: Get from auth token
    db: Session = Depends(get_db)
):
    """
    Unlike a post
    
    Args:
        post_id: Post ID
        user_id: Current user ID
        db: Database session
    
    Returns:
        Success message
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    like = db.query(PostLike).filter(
        PostLike.post_id == post_id,
        PostLike.user_id == user_id
    ).first()
    
    if not like:
        raise HTTPException(status_code=400, detail="Post not liked")
    
    # Update post likes count
    post.likes_count = max(0, post.likes_count - 1)
    
    db.delete(like)
    db.commit()
    
    return {"message": "Post unliked", "likes_count": post.likes_count}


@router.post("/posts/{post_id}/comments", response_model=CommentResponse)
async def add_comment(
    post_id: str,
    comment_data: CommentCreate,
    user_id: str = Query(default="anonymous", description="User ID"),  # TODO: Get from auth token
    db: Session = Depends(get_db)
):
    """
    Add a comment to a post
    
    Args:
        post_id: Post ID
        comment_data: Comment content
        user_id: Current user ID
        db: Database session
    
    Returns:
        Created comment
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    comment = PostComment(
        id=str(uuid.uuid4()),
        post_id=post_id,
        user_id=user_id,
        content=comment_data.content
    )
    
    # Update post comments count
    post.comments_count += 1
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return CommentResponse(**comment.to_dict())


# ==================== FRIENDS ====================

@router.post("/friends/request", response_model=FriendResponse)
async def send_friend_request(
    request_data: FriendRequest,
    user_id: str = Query(default="anonymous", description="User ID"),  # TODO: Get from auth token
    db: Session = Depends(get_db)
):
    """
    Send a friend request
    
    Args:
        request_data: Friend request data
        user_id: Current user ID
        db: Database session
    
    Returns:
        Created friend request
    """
    friend_id = request_data.friend_id
    
    if user_id == friend_id:
        raise HTTPException(status_code=400, detail="Cannot friend yourself")
    
    # Check if already friends
    existing = db.query(Friend).filter(
        ((Friend.user_id == user_id) & (Friend.friend_id == friend_id)) |
        ((Friend.user_id == friend_id) & (Friend.friend_id == user_id))
    ).first()
    
    if existing:
        if existing.status == FriendStatus.ACCEPTED.value:
            raise HTTPException(status_code=400, detail="Already friends")
        elif existing.status == FriendStatus.PENDING.value:
            raise HTTPException(status_code=400, detail="Friend request already pending")
    
    friend = Friend(
        id=str(uuid.uuid4()),
        user_id=user_id,
        friend_id=friend_id,
        status=FriendStatus.PENDING.value
    )
    
    db.add(friend)
    db.commit()
    db.refresh(friend)
    
    return FriendResponse(**friend.to_dict())


@router.post("/friends/{friend_id}/accept")
async def accept_friend_request(
    friend_id: str,
    user_id: str = Query(default="anonymous", description="User ID"),  # TODO: Get from auth token
    db: Session = Depends(get_db)
):
    """
    Accept a friend request
    
    Args:
        friend_id: Friend ID who sent the request
        user_id: Current user ID
        db: Database session
    
    Returns:
        Success message
    """
    friend = db.query(Friend).filter(
        Friend.user_id == friend_id,
        Friend.friend_id == user_id,
        Friend.status == FriendStatus.PENDING.value
    ).first()
    
    if not friend:
        raise HTTPException(status_code=404, detail="Friend request not found")
    
    friend.status = FriendStatus.ACCEPTED.value
    
    # Create reverse relationship
    reverse_friend = Friend(
        id=str(uuid.uuid4()),
        user_id=user_id,
        friend_id=friend_id,
        status=FriendStatus.ACCEPTED.value
    )
    
    db.add(reverse_friend)
    db.commit()
    
    return {"message": "Friend request accepted"}


@router.get("/friends", response_model=FriendListResponse)
async def get_friends(
    user_id: str = Query(default="anonymous", description="User ID"),  # TODO: Get from auth token
    db: Session = Depends(get_db)
):
    """
    Get list of friends
    
    Args:
        user_id: Current user ID
        db: Database session
    
    Returns:
        List of friends
    """
    friends = db.query(Friend).filter(
        Friend.user_id == user_id,
        Friend.status == FriendStatus.ACCEPTED.value
    ).all()
    
    return FriendListResponse(
        friends=[FriendResponse(**f.to_dict()) for f in friends],
        count=len(friends)
    )


@router.get("/friends/requests", response_model=FriendListResponse)
async def get_friend_requests(
    user_id: str = Query(default="anonymous", description="User ID"),  # TODO: Get from auth token
    db: Session = Depends(get_db)
):
    """
    Get pending friend requests
    
    Args:
        user_id: Current user ID
        db: Database session
    
    Returns:
        List of pending friend requests
    """
    requests = db.query(Friend).filter(
        Friend.friend_id == user_id,
        Friend.status == FriendStatus.PENDING.value
    ).all()
    
    return FriendListResponse(
        friends=[FriendResponse(**f.to_dict()) for f in requests],
        count=len(requests)
    )


# ==================== USERS ====================

@router.get("/users/directory")
async def get_user_directory(
    user_id: str = Query(default="anonymous", description="User ID"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get directory of all users in the system
    
    Args:
        user_id: Current user ID
        limit: Maximum number of users
        offset: Pagination offset
        db: Database session
    
    Returns:
        List of users with basic info
    """
    try:
        # Get all unique user IDs from posts, friends, and insights
        from sqlalchemy import func, distinct
        
        # Get users from posts
        post_users = db.query(Post.author_id).distinct().all()
        # Get users from friends (both user_id and friend_id)
        friend_user_ids = db.query(Friend.user_id).distinct().all()
        friend_friend_ids = db.query(Friend.friend_id).distinct().all()
        # Get users from insights
        insight_users = db.query(Insight.user_id).distinct().all()
        
        # Combine and get unique user IDs
        all_user_ids = set()
        for row in post_users:
            if row[0]:
                all_user_ids.add(row[0])
        for row in friend_user_ids:
            if row[0]:
                all_user_ids.add(row[0])
        for row in friend_friend_ids:
            if row[0]:
                all_user_ids.add(row[0])
        for row in insight_users:
            if row[0]:
                all_user_ids.add(row[0])
        
        # Convert to list and paginate
        user_ids_list = sorted(list(all_user_ids))[offset:offset+limit]
        
        # Build user directory with stats
        users = []
        for uid in user_ids_list:
            # Get user stats
            posts_count = db.query(func.count(Post.id)).filter(Post.author_id == uid).scalar() or 0
            friends_count = db.query(func.count(Friend.id)).filter(
                Friend.user_id == uid,
                Friend.status == FriendStatus.ACCEPTED.value
            ).scalar() or 0
            insights_count = db.query(func.count(Insight.id)).filter(Insight.user_id == uid).scalar() or 0
            
            # Check if current user is friends with this user
            is_friend = False
            if user_id != "anonymous" and user_id != uid:
                friend_relation = db.query(Friend).filter(
                    ((Friend.user_id == user_id) & (Friend.friend_id == uid)) |
                    ((Friend.user_id == uid) & (Friend.friend_id == user_id)),
                    Friend.status == FriendStatus.ACCEPTED.value
                ).first()
                is_friend = friend_relation is not None
            
            # Check if there's a pending request
            has_pending_request = False
            if user_id != "anonymous" and user_id != uid:
                pending = db.query(Friend).filter(
                    ((Friend.user_id == user_id) & (Friend.friend_id == uid)) |
                    ((Friend.user_id == uid) & (Friend.friend_id == user_id)),
                    Friend.status == FriendStatus.PENDING.value
                ).first()
                has_pending_request = pending is not None
            
            users.append({
                "user_id": uid,
                "posts_count": posts_count,
                "friends_count": friends_count,
                "insights_count": insights_count,
                "is_friend": is_friend,
                "has_pending_request": has_pending_request,
            })
        
        return {
            "users": users,
            "count": len(users),
            "total": len(all_user_ids),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error getting user directory: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting user directory: {str(e)}"
        )


@router.get("/users/{target_user_id}/profile")
async def get_user_profile(
    target_user_id: str,
    user_id: str = Query(default="anonymous", description="Current user ID"),
    db: Session = Depends(get_db)
):
    """
    Get user profile information
    
    Args:
        target_user_id: User ID to get profile for
        user_id: Current user ID
        db: Database session
    
    Returns:
        User profile with stats and recent posts
    """
    try:
        from sqlalchemy import func
        
        # Get user stats
        posts_count = db.query(func.count(Post.id)).filter(Post.author_id == target_user_id).scalar() or 0
        friends_count = db.query(func.count(Friend.id)).filter(
            Friend.user_id == target_user_id,
            Friend.status == FriendStatus.ACCEPTED.value
        ).scalar() or 0
        insights_count = db.query(func.count(Insight.id)).filter(Insight.user_id == target_user_id).scalar() or 0
        
        # Get recent posts (limit 10)
        recent_posts = db.query(Post).filter(
            Post.author_id == target_user_id
        ).order_by(Post.created_at.desc()).limit(10).all()
        
        # Check friendship status
        is_friend = False
        has_pending_request = False
        if user_id != "anonymous" and user_id != target_user_id:
            friend_relation = db.query(Friend).filter(
                ((Friend.user_id == user_id) & (Friend.friend_id == target_user_id)) |
                ((Friend.user_id == target_user_id) & (Friend.friend_id == user_id))
            ).first()
            if friend_relation:
                if friend_relation.status == FriendStatus.ACCEPTED.value:
                    is_friend = True
                elif friend_relation.status == FriendStatus.PENDING.value:
                    has_pending_request = True
        
        return {
            "user_id": target_user_id,
            "posts_count": posts_count,
            "friends_count": friends_count,
            "insights_count": insights_count,
            "is_friend": is_friend,
            "has_pending_request": has_pending_request,
            "recent_posts": [PostResponse(**p.to_dict()) for p in recent_posts]
        }
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting user profile: {str(e)}"
        )

