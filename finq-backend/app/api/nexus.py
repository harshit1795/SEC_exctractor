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
from app.models.user_profile import UserProfile
from app.api.websocket import broadcast_new_post
from app.schemas.nexus import (
    PostCreate, PostResponse, PostListResponse, AuthorInfo,
    FriendRequest, FriendResponse, FriendListResponse,
    CommentCreate, CommentResponse,
    UserProfileUpdate, UserProfileResponse, UserProfileInitialize
)
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/nexus", tags=["nexus"])


def get_or_create_user_profile(user_id: str, db: Session, firebase_display_name: Optional[str] = None, firebase_photo_url: Optional[str] = None) -> UserProfile:
    """
    Get or create user profile if it doesn't exist
    
    Args:
        user_id: User ID
        db: Database session
        firebase_display_name: Optional Firebase display name
        firebase_photo_url: Optional Firebase photo URL
    
    Returns:
        UserProfile instance
    """
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if not profile:
        # Create default profile with Firebase data if provided
        profile = UserProfile(
            id=str(uuid.uuid4()),
            user_id=user_id,
            display_name=None,
            firebase_display_name=firebase_display_name,
            profile_picture_url=None,
            firebase_photo_url=firebase_photo_url,
            use_alias_as_display=False
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    elif firebase_display_name and not profile.firebase_display_name:
        # Update Firebase data if not already set
        profile.firebase_display_name = firebase_display_name
        if firebase_photo_url and not profile.firebase_photo_url:
            profile.firebase_photo_url = firebase_photo_url
        db.commit()
        db.refresh(profile)
    
    return profile


def get_user_display_info(user_id: str, db: Session) -> dict:
    """
    Get user display information based on their profile preferences
    
    Returns:
        dict with display_name, profile_picture_url, firebase_display_name, firebase_photo_url
    """
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if not profile:
        # If no profile exists, try to create one (this handles users who haven't initialized their profile)
        # But we can't create it here without Firebase data, so return None
        return {
            "display_name": None,
            "profile_picture_url": None,
            "firebase_display_name": None,
            "firebase_photo_url": None
        }
    
    # Determine effective display name based on user preferences
    if profile.use_alias_as_display and profile.display_name:
        # User wants to use alias as display name
        effective_display_name = profile.display_name
    elif profile.firebase_display_name:
        # Use Firebase display name if available (even if alias exists but not using it)
        effective_display_name = profile.firebase_display_name
    elif profile.display_name:
        # Fallback to alias if no Firebase name
        effective_display_name = profile.display_name
    else:
        # No display name available
        effective_display_name = None
    
    # Determine effective profile picture
    effective_profile_picture = profile.profile_picture_url or profile.firebase_photo_url
    
    return {
        "display_name": effective_display_name,
        "profile_picture_url": effective_profile_picture,
        "firebase_display_name": profile.firebase_display_name,
        "firebase_photo_url": profile.firebase_photo_url
    }


# ==================== POSTS ====================

@router.post("/posts", response_model=PostResponse)
async def create_post(
    post_data: PostCreate,
    user_id: str = Query(..., description="User ID (Firebase UID)"),  # Required - must be provided from frontend
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
    user_id: str = Query(..., description="User ID (Firebase UID)"),  # Required - must be provided from frontend
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
        # Get list of friend IDs (check both directions: user_id->friend_id and friend_id->user_id)
        friends_as_user = db.query(Friend).filter(
            Friend.user_id == user_id,
            Friend.status == FriendStatus.ACCEPTED.value
        ).all()
        
        friends_as_friend = db.query(Friend).filter(
            Friend.friend_id == user_id,
            Friend.status == FriendStatus.ACCEPTED.value
        ).all()
        
        # Combine friend IDs from both directions
        friend_ids = set()
        for f in friends_as_user:
            friend_ids.add(f.friend_id)
        for f in friends_as_friend:
            friend_ids.add(f.user_id)
        
        friend_ids.add(user_id)  # Include own posts
        friend_ids = list(friend_ids)
        
        # Get posts from friends
        posts = db.query(Post).filter(
            Post.author_id.in_(friend_ids)
        ).order_by(
            Post.created_at.desc()
        ).limit(limit).offset(offset).all()
        
        # Get like status for each post and add author info
        post_responses = []
        for post in posts:
            post_dict = post.to_dict()
            # Check if user liked this post
            like = db.query(PostLike).filter(
                PostLike.post_id == post.id,
                PostLike.user_id == user_id
            ).first()
            post_dict["liked"] = like is not None
            
            # Get author display information
            author_info = get_user_display_info(post.author_id, db)
            # Ensure we always have a display name (use display_name from profile, fallback to firebase_display_name, then user_id)
            effective_display_name = (
                author_info.get("display_name") 
                or author_info.get("firebase_display_name") 
                or post.author_id
            )
            post_dict["author"] = {
                "user_id": post.author_id,
                "display_name": effective_display_name,
                "profile_picture_url": author_info.get("profile_picture_url") or author_info.get("firebase_photo_url"),
                "firebase_display_name": author_info.get("firebase_display_name")
            }
            
            # Get comments with author info
            comments = db.query(PostComment).filter(
                PostComment.post_id == post.id
            ).order_by(PostComment.created_at.desc()).all()
            comment_dicts = []
            for comment in comments:
                comment_dict = comment.to_dict()
                comment_author_info = get_user_display_info(comment.user_id, db)
                # Ensure we always have a display name
                comment_effective_display_name = (
                    comment_author_info.get("display_name") 
                    or comment_author_info.get("firebase_display_name") 
                    or comment.user_id
                )
                comment_dict["author"] = {
                    "user_id": comment.user_id,
                    "display_name": comment_effective_display_name,
                    "profile_picture_url": comment_author_info.get("profile_picture_url") or comment_author_info.get("firebase_photo_url"),
                    "firebase_display_name": comment_author_info.get("firebase_display_name")
                }
                comment_dicts.append(comment_dict)
            post_dict["comments"] = comment_dicts
            
            # Convert to PostResponse (which will validate the author field)
            post_responses.append(PostResponse(**post_dict))
        
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
    db: Session = Depends(get_db)
):
    """
    Send a friend request
    
    Args:
        request_data: Friend request data (contains user_id and friend_id)
        db: Database session
    
    Returns:
        Created friend request
    """
    user_id = request_data.user_id
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
    user_id: str = Query(..., description="User ID (Firebase UID)"),  # Required - must be provided from frontend
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
    user_id: str = Query(..., description="User ID (Firebase UID)"),  # Required - must be provided from frontend
    db: Session = Depends(get_db)
):
    """
    Get list of friends
    
    Args:
        user_id: Current user ID
        db: Database session
    
    Returns:
        List of friends with display information
    """
    # Get friends from both directions (user_id->friend_id and friend_id->user_id)
    friends_as_user = db.query(Friend).filter(
        Friend.user_id == user_id,
        Friend.status == FriendStatus.ACCEPTED.value
    ).all()
    
    friends_as_friend = db.query(Friend).filter(
        Friend.friend_id == user_id,
        Friend.status == FriendStatus.ACCEPTED.value
    ).all()
    
    # Combine and get unique friend IDs
    all_friends = []
    friend_ids_seen = set()
    
    for f in friends_as_user:
        if f.friend_id not in friend_ids_seen and f.friend_id != user_id and f.friend_id != "anonymous":
            all_friends.append(f)
            friend_ids_seen.add(f.friend_id)
    
    for f in friends_as_friend:
        if f.user_id not in friend_ids_seen and f.user_id != user_id and f.user_id != "anonymous":
            all_friends.append(f)
            friend_ids_seen.add(f.user_id)
    
    # Enrich friends with display information
    enriched_friends = []
    for f in all_friends:
        friend_id = f.friend_id if f.user_id == user_id else f.user_id
        display_info = get_user_display_info(friend_id, db)
        
        friend_dict = f.to_dict()
        friend_dict['display_name'] = display_info.get("display_name") or display_info.get("firebase_display_name")
        friend_dict['profile_picture_url'] = display_info.get("profile_picture_url") or display_info.get("firebase_photo_url")
        enriched_friends.append(FriendResponse(**friend_dict))
    
    return FriendListResponse(
        friends=enriched_friends,
        count=len(enriched_friends)
    )


@router.get("/friends/requests", response_model=FriendListResponse)
async def get_friend_requests(
    user_id: str = Query(..., description="User ID (Firebase UID)"),  # Required - must be provided from frontend
    db: Session = Depends(get_db)
):
    """
    Get pending friend requests
    
    Args:
        user_id: Current user ID
        db: Database session
    
    Returns:
        List of pending friend requests with display information
    """
    requests = db.query(Friend).filter(
        Friend.friend_id == user_id,
        Friend.status == FriendStatus.PENDING.value
    ).all()
    
    # Enrich requests with display information
    enriched_requests = []
    for req in requests:
        # The user who sent the request is in req.user_id
        requester_id = req.user_id
        display_info = get_user_display_info(requester_id, db)
        
        request_dict = req.to_dict()
        request_dict['display_name'] = display_info.get("display_name") or display_info.get("firebase_display_name")
        request_dict['profile_picture_url'] = display_info.get("profile_picture_url") or display_info.get("firebase_photo_url")
        request_dict['firebase_display_name'] = display_info.get("firebase_display_name")
        enriched_requests.append(FriendResponse(**request_dict))
    
    return FriendListResponse(
        friends=enriched_requests,
        count=len(enriched_requests)
    )


# ==================== USERS ====================

@router.get("/users/directory")
async def get_user_directory(
    user_id: str = Query(..., description="User ID (Firebase UID)"),  # Required - must be provided from frontend
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
        # Get all unique user IDs from posts, friends, insights, and user_profiles
        from sqlalchemy import func, distinct
        
        # Get users from posts
        post_users = db.query(Post.author_id).distinct().all()
        # Get users from friends (both user_id and friend_id)
        friend_user_ids = db.query(Friend.user_id).distinct().all()
        friend_friend_ids = db.query(Friend.friend_id).distinct().all()
        # Get users from insights
        insight_users = db.query(Insight.user_id).distinct().all()
        # Get users from user_profiles (all authenticated users)
        profile_users = db.query(UserProfile.user_id).distinct().all()
        
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
        for row in profile_users:
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
            
            # Check if there's a pending request and who sent it
            has_pending_request = False
            pending_request_sent_by_me = False
            if user_id and user_id != uid:
                # Check if current user sent a request to this user
                pending_sent_by_me = db.query(Friend).filter(
                    Friend.user_id == user_id,
                    Friend.friend_id == uid,
                    Friend.status == FriendStatus.PENDING.value
                ).first()
                
                # Check if this user sent a request to current user
                pending_sent_to_me = db.query(Friend).filter(
                    Friend.user_id == uid,
                    Friend.friend_id == user_id,
                    Friend.status == FriendStatus.PENDING.value
                ).first()
                
                if pending_sent_by_me:
                    has_pending_request = True
                    pending_request_sent_by_me = True
                elif pending_sent_to_me:
                    has_pending_request = True
                    pending_request_sent_by_me = False
            
            # Get user display information
            display_info = get_user_display_info(uid, db)
            
            users.append({
                "user_id": uid,
                "display_name": display_info.get("display_name") or display_info.get("firebase_display_name"),
                "profile_picture_url": display_info.get("profile_picture_url") or display_info.get("firebase_photo_url"),
                "firebase_display_name": display_info.get("firebase_display_name"),
                "posts_count": posts_count,
                "friends_count": friends_count,
                "insights_count": insights_count,
                "is_friend": is_friend,
                "has_pending_request": has_pending_request,
                "pending_request_sent_by_me": pending_request_sent_by_me,
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
    user_id: str = Query(default="anonymous", description="Current user ID (Firebase UID)"),
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
        pending_request_sent_by_me = False
        if user_id and user_id != "anonymous" and user_id != target_user_id:
            # Check if already friends
            friend_relation = db.query(Friend).filter(
                ((Friend.user_id == user_id) & (Friend.friend_id == target_user_id)) |
                ((Friend.user_id == target_user_id) & (Friend.friend_id == user_id)),
                Friend.status == FriendStatus.ACCEPTED.value
            ).first()
            
            if friend_relation:
                is_friend = True
            else:
                # Check if current user sent a request to this user
                pending_sent_by_me = db.query(Friend).filter(
                    Friend.user_id == user_id,
                    Friend.friend_id == target_user_id,
                    Friend.status == FriendStatus.PENDING.value
                ).first()
                
                # Check if this user sent a request to current user
                pending_sent_to_me = db.query(Friend).filter(
                    Friend.user_id == target_user_id,
                    Friend.friend_id == user_id,
                    Friend.status == FriendStatus.PENDING.value
                ).first()
                
                if pending_sent_by_me:
                    has_pending_request = True
                    pending_request_sent_by_me = True
                elif pending_sent_to_me:
                    has_pending_request = True
                    pending_request_sent_by_me = False
        
        # Get user profile display information
        display_info = get_user_display_info(target_user_id, db)
        
        return {
            "user_id": target_user_id,
            "display_name": display_info.get("display_name") or display_info.get("firebase_display_name"),
            "profile_picture_url": display_info.get("profile_picture_url") or display_info.get("firebase_photo_url"),
            "firebase_display_name": display_info.get("firebase_display_name"),
            "posts_count": posts_count,
            "friends_count": friends_count,
            "insights_count": insights_count,
            "is_friend": is_friend,
            "has_pending_request": has_pending_request,
            "pending_request_sent_by_me": pending_request_sent_by_me,
            "recent_posts": [PostResponse(**p.to_dict()) for p in recent_posts]
        }
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting user profile: {str(e)}"
        )


# ==================== USER PROFILE MANAGEMENT ====================

@router.post("/users/{target_user_id}/profile/initialize", response_model=UserProfileResponse)
async def initialize_user_profile(
    target_user_id: str,
    init_data: Optional[UserProfileInitialize] = None,
    user_id: str = Query(default="anonymous", description="Current user ID"),
    db: Session = Depends(get_db)
):
    """
    Initialize/create user profile on first sign-in
    
    Args:
        target_user_id: User ID to initialize profile for
        init_data: Optional Firebase user data (display name, photo URL, email)
        user_id: Current user ID (must match target_user_id)
        db: Database session
    
    Returns:
        Created user profile
    """
    try:
        # Only allow users to initialize their own profile
        if user_id != target_user_id:
            raise HTTPException(
                status_code=403,
                detail="You can only initialize your own profile"
            )
        
        profile = get_or_create_user_profile(
            target_user_id, 
            db,
            firebase_display_name=init_data.firebase_display_name if init_data else None,
            firebase_photo_url=init_data.firebase_photo_url if init_data else None
        )
        
        # If Firebase data is provided and profile doesn't have custom settings, use Firebase data
        if init_data:
            if init_data.firebase_photo_url and not profile.profile_picture_url:
                profile.profile_picture_url = init_data.firebase_photo_url
            # Store Firebase display name for reference (user can override with alias)
            if init_data.firebase_display_name and not profile.firebase_display_name:
                profile.firebase_display_name = init_data.firebase_display_name
        
        db.commit()
        db.refresh(profile)
        
        return UserProfileResponse(**profile.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initializing user profile: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error initializing user profile: {str(e)}"
        )


@router.get("/users/{target_user_id}/profile/preferences", response_model=UserProfileResponse)
async def get_user_profile_preferences(
    target_user_id: str,
    user_id: str = Query(default="anonymous", description="Current user ID (Firebase UID)"),
    db: Session = Depends(get_db)
):
    """
    Get user profile preferences
    
    Args:
        target_user_id: User ID to get profile for
        user_id: Current user ID (Firebase UID)
        db: Database session
    
    Returns:
        User profile preferences
    """
    try:
        profile = get_or_create_user_profile(target_user_id, db)
        return UserProfileResponse(**profile.to_dict())
        
    except Exception as e:
        logger.error(f"Error getting user profile preferences: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting user profile preferences: {str(e)}"
        )


@router.put("/users/{target_user_id}/profile/preferences", response_model=UserProfileResponse)
async def update_user_profile_preferences(
    target_user_id: str,
    profile_data: UserProfileUpdate,
    user_id: str = Query(default="anonymous", description="Current user ID"),  # TODO: Get from auth token
    db: Session = Depends(get_db)
):
    """
    Update user profile preferences
    
    Args:
        target_user_id: User ID to update profile for
        profile_data: Profile data to update
        user_id: Current user ID (must match target_user_id)
        db: Database session
    
    Returns:
        Updated user profile
    """
    try:
        # Only allow users to update their own profile
        if user_id != target_user_id:
            raise HTTPException(
                status_code=403,
                detail="You can only update your own profile"
            )
        
        profile = get_or_create_user_profile(target_user_id, db)
        
        if profile:
            # Update existing profile
            if profile_data.display_name is not None:
                profile.display_name = profile_data.display_name
            if profile_data.profile_picture_url is not None:
                profile.profile_picture_url = profile_data.profile_picture_url
            if profile_data.use_alias_as_display is not None:
                profile.use_alias_as_display = profile_data.use_alias_as_display
        
        db.commit()
        db.refresh(profile)
        
        return UserProfileResponse(**profile.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile preferences: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error updating user profile preferences: {str(e)}"
        )

