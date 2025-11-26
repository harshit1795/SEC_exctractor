"""
Migration script to copy data from Firebase Firestore to PostgreSQL/SQLite

This script migrates:
- Posts (from 'posts' collection)
- Friends (from 'users' collection friends arrays and 'friend_requests' collection)
- Post likes (from posts.likes arrays)
- Post comments (from posts.comments arrays)

Usage:
    python finq-backend/scripts/migrate_firestore.py

Requirements:
    - Firebase credentials file: firebase-credentials.json (in project root)
    - Or set FIREBASE_CREDENTIALS_JSON environment variable
    - PostgreSQL/SQLite database configured in .env
"""

import sys
import os
import json
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Firebase imports
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    print("ERROR: firebase-admin not installed. Install with: pip install firebase-admin")
    sys.exit(1)

# SQLAlchemy imports
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models.post import Post, PostLike, PostComment
from app.models.friend import Friend, FriendStatus
from app.config import settings

# Initialize logger
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_toml_secrets(secrets_path: Path) -> Optional[Dict]:
    """Try to load Firebase credentials from Streamlit secrets.toml"""
    try:
        import toml
        with open(secrets_path) as f:
            secrets = toml.load(f)
        
        # Try different possible secret keys
        if "firebase" in secrets and "service_account" in secrets["firebase"]:
            return secrets["firebase"]["service_account"]
        elif "FIREBASE_CREDENTIALS_B64" in secrets:
            # Decode base64 encoded credentials
            creds_b64_str = secrets["FIREBASE_CREDENTIALS_B64"]
            creds_json_str = base64.b64decode(creds_b64_str).decode('utf-8')
            return json.loads(creds_json_str)
        elif "firebase_credentials" in secrets:
            return secrets["firebase_credentials"]
    except ImportError:
        logger.warning("toml library not installed. Install with: pip install toml")
    except Exception as e:
        logger.warning(f"Failed to load secrets from {secrets_path}: {e}")
    return None


def init_firestore():
    """Initialize Firestore client"""
    if firebase_admin._apps:
        logger.info("Firebase already initialized")
        return firestore.client()
    
    # Try to get credentials from environment variable
    creds_dict = None
    firebase_creds_json = os.environ.get("FIREBASE_CREDENTIALS_JSON")
    if firebase_creds_json:
        try:
            creds_dict = json.loads(firebase_creds_json)
            logger.info("Loaded Firebase credentials from FIREBASE_CREDENTIALS_JSON environment variable")
        except json.JSONDecodeError:
            logger.error("Failed to parse FIREBASE_CREDENTIALS_JSON")
            return None
    
    # Try base64 encoded environment variable (like Streamlit Cloud)
    if not creds_dict:
        firebase_creds_b64 = os.environ.get("FIREBASE_CREDENTIALS_B64")
        if firebase_creds_b64:
            try:
                creds_json_str = base64.b64decode(firebase_creds_b64).decode('utf-8')
                creds_dict = json.loads(creds_json_str)
                logger.info("Loaded Firebase credentials from FIREBASE_CREDENTIALS_B64 environment variable")
            except Exception as e:
                logger.warning(f"Failed to decode FIREBASE_CREDENTIALS_B64: {e}")
    
    # Try to load from Streamlit secrets.toml
    if not creds_dict:
        project_root = Path(__file__).parent.parent.parent
        secrets_paths = [
            project_root / ".streamlit" / "secrets.toml",
            project_root / "secrets.toml",
            Path.cwd() / ".streamlit" / "secrets.toml",
            Path.cwd() / "secrets.toml",
        ]
        
        for secrets_path in secrets_paths:
            if secrets_path.exists():
                logger.info(f"Found secrets file at {secrets_path}, attempting to load...")
                creds_dict = load_toml_secrets(secrets_path)
                if creds_dict:
                    logger.info(f"Loaded Firebase credentials from {secrets_path}")
                    break
    
    # Try to load from JSON files
    if not creds_dict:
        creds_paths = [
            Path(__file__).parent.parent.parent / "firebase-credentials.json",
            Path(__file__).parent.parent.parent / "firebase_credentials.json",
            Path.cwd() / "firebase-credentials.json",
            Path.cwd() / "firebase_credentials.json",
            Path.home() / "firebase-credentials.json",
        ]
        
        for creds_path in creds_paths:
            if creds_path.exists():
                try:
                    with open(creds_path) as f:
                        creds_dict = json.load(f)
                    logger.info(f"Loaded Firebase credentials from {creds_path}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to load {creds_path}: {e}")
                    continue
    
    if not creds_dict:
        logger.error("=" * 60)
        logger.error("Firebase credentials not found!")
        logger.error("=" * 60)
        logger.error("Please provide credentials using one of these methods:")
        logger.error("")
        logger.error("1. Environment Variable (JSON string):")
        logger.error("   export FIREBASE_CREDENTIALS_JSON='{\"type\":\"service_account\",...}'")
        logger.error("")
        logger.error("2. Environment Variable (Base64 encoded):")
        logger.error("   export FIREBASE_CREDENTIALS_B64='<base64-encoded-json>'")
        logger.error("")
        logger.error("3. JSON File in project root:")
        logger.error("   Place firebase-credentials.json in: /Users/harshitgola/Projects/SEC_exctractor/SEC_exctractor/")
        logger.error("")
        logger.error("4. Streamlit secrets.toml:")
        logger.error("   Place .streamlit/secrets.toml with firebase.service_account or FIREBASE_CREDENTIALS_B64")
        logger.error("")
        logger.error("To get Firebase credentials:")
        logger.error("  1. Go to Firebase Console > Project Settings > Service Accounts")
        logger.error("  2. Click 'Generate New Private Key'")
        logger.error("  3. Download the JSON file")
        logger.error("=" * 60)
        return None
    
    try:
        cred = credentials.Certificate(creds_dict)
        firebase_admin.initialize_app(cred)
        logger.info("Firebase initialized successfully")
        return firestore.client()
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        logger.error("Please verify your credentials are valid.")
        return None


def convert_timestamp(firestore_timestamp) -> Optional[datetime]:
    """Convert Firestore timestamp to Python datetime"""
    if firestore_timestamp is None:
        return None
    
    # Firestore timestamp object
    if hasattr(firestore_timestamp, 'timestamp'):
        return datetime.fromtimestamp(firestore_timestamp.timestamp())
    
    # Already a datetime
    if isinstance(firestore_timestamp, datetime):
        return firestore_timestamp
    
    # String format
    if isinstance(firestore_timestamp, str):
        try:
            return datetime.fromisoformat(firestore_timestamp.replace('Z', '+00:00'))
        except:
            pass
    
    return None


def migrate_posts(db: Session, firestore_db) -> Dict[str, int]:
    """Migrate posts from Firestore to PostgreSQL"""
    logger.info("=" * 60)
    logger.info("Migrating Posts...")
    logger.info("=" * 60)
    
    stats = {"migrated": 0, "skipped": 0, "errors": 0}
    
    try:
        posts_ref = firestore_db.collection('posts')
        posts = list(posts_ref.stream())
        logger.info(f"Found {len(posts)} posts in Firestore")
        
        for doc in posts:
            try:
                post_data = doc.to_dict()
                post_id = doc.id
                
                # Check if post already exists
                existing = db.query(Post).filter(Post.id == post_id).first()
                if existing:
                    logger.debug(f"Post {post_id} already exists, skipping")
                    stats["skipped"] += 1
                    continue
                
                # Extract data
                author_id = post_data.get('authorId') or post_data.get('author_id')
                if not author_id:
                    logger.warning(f"Post {post_id} has no authorId, skipping")
                    stats["skipped"] += 1
                    continue
                
                content = post_data.get('content', '')
                timestamp = convert_timestamp(post_data.get('timestamp'))
                created_at = timestamp or datetime.now()
                
                # Extract likes and comments (will be migrated separately)
                likes = post_data.get('likes', [])
                comments = post_data.get('comments', [])
                
                # Create post
                post = Post(
                    id=post_id,
                    author_id=author_id,
                    content=content,
                    media_urls=post_data.get('media_urls', []) or [],
                    media_type=post_data.get('media_type'),
                    likes_count=len(likes) if isinstance(likes, list) else 0,
                    comments_count=len(comments) if isinstance(comments, list) else 0,
                    shares_count=post_data.get('shares_count', 0) or 0,
                    is_shared_insight=post_data.get('is_shared_insight', False) or False,
                    insight_id=post_data.get('insight_id'),
                    tags=post_data.get('tags', []) or [],
                    created_at=created_at,
                )
                
                db.add(post)
                db.flush()  # Flush to get the post ID
                
                # Migrate likes
                if isinstance(likes, list):
                    for like_user_id in likes:
                        if like_user_id:
                            # Check if like already exists
                            existing_like = db.query(PostLike).filter(
                                PostLike.post_id == post_id,
                                PostLike.user_id == like_user_id
                            ).first()
                            if not existing_like:
                                like = PostLike(
                                    post_id=post_id,
                                    user_id=like_user_id,
                                    created_at=created_at,
                                )
                                db.add(like)
                
                # Migrate comments
                if isinstance(comments, list):
                    for comment_data in comments:
                        if isinstance(comment_data, dict):
                            comment_user_id = comment_data.get('userId') or comment_data.get('user_id')
                            comment_text = comment_data.get('text') or comment_data.get('content', '')
                            comment_timestamp = convert_timestamp(comment_data.get('timestamp'))
                            
                            if comment_user_id and comment_text:
                                comment = PostComment(
                                    post_id=post_id,
                                    user_id=comment_user_id,
                                    content=comment_text,
                                    created_at=comment_timestamp or created_at,
                                )
                                db.add(comment)
                
                stats["migrated"] += 1
                if stats["migrated"] % 10 == 0:
                    logger.info(f"Migrated {stats['migrated']} posts...")
                    db.commit()
                
            except Exception as e:
                logger.error(f"Error migrating post {doc.id}: {e}")
                stats["errors"] += 1
                db.rollback()
                continue
        
        db.commit()
        logger.info(f"Posts migration complete: {stats['migrated']} migrated, {stats['skipped']} skipped, {stats['errors']} errors")
        
    except Exception as e:
        logger.error(f"Error in posts migration: {e}")
        db.rollback()
        stats["errors"] += 1
    
    return stats


def migrate_friends(db: Session, firestore_db) -> Dict[str, int]:
    """Migrate friends from Firestore to PostgreSQL"""
    logger.info("=" * 60)
    logger.info("Migrating Friends...")
    logger.info("=" * 60)
    
    stats = {"migrated": 0, "skipped": 0, "errors": 0}
    
    try:
        # First, migrate friend requests
        logger.info("Migrating friend requests...")
        requests_ref = firestore_db.collection('friend_requests')
        requests = list(requests_ref.stream())
        logger.info(f"Found {len(requests)} friend requests in Firestore")
        
        for doc in requests:
            try:
                request_data = doc.to_dict()
                from_user_id = request_data.get('fromUserId') or request_data.get('from_user_id')
                to_user_id = request_data.get('toUserId') or request_data.get('to_user_id')
                status = request_data.get('status', 'pending')
                
                if not from_user_id or not to_user_id:
                    logger.warning(f"Friend request {doc.id} missing user IDs, skipping")
                    stats["skipped"] += 1
                    continue
                
                # Map status
                if status == 'accepted':
                    friend_status = FriendStatus.ACCEPTED.value
                elif status == 'rejected':
                    stats["skipped"] += 1  # Skip rejected requests
                    continue
                else:
                    friend_status = FriendStatus.PENDING.value
                
                # Check if relationship already exists
                existing = db.query(Friend).filter(
                    ((Friend.user_id == from_user_id) & (Friend.friend_id == to_user_id)) |
                    ((Friend.user_id == to_user_id) & (Friend.friend_id == from_user_id))
                ).first()
                
                if existing:
                    logger.debug(f"Friend relationship already exists: {from_user_id} <-> {to_user_id}")
                    stats["skipped"] += 1
                    continue
                
                # Create friend relationship (one direction)
                friend = Friend(
                    user_id=from_user_id,
                    friend_id=to_user_id,
                    status=friend_status,
                    created_at=convert_timestamp(request_data.get('timestamp')) or datetime.now(),
                )
                db.add(friend)
                
                # If accepted, create reverse relationship
                if friend_status == FriendStatus.ACCEPTED.value:
                    friend_reverse = Friend(
                        user_id=to_user_id,
                        friend_id=from_user_id,
                        status=FriendStatus.ACCEPTED.value,
                        created_at=friend.created_at,
                    )
                    db.add(friend_reverse)
                
                stats["migrated"] += 1
                if stats["migrated"] % 10 == 0:
                    logger.info(f"Migrated {stats['migrated']} friend relationships...")
                    db.commit()
                
            except Exception as e:
                logger.error(f"Error migrating friend request {doc.id}: {e}")
                stats["errors"] += 1
                db.rollback()
                continue
        
        # Second, migrate friends from user profiles
        logger.info("Migrating friends from user profiles...")
        users_ref = firestore_db.collection('users')
        users = list(users_ref.stream())
        logger.info(f"Found {len(users)} users in Firestore")
        
        for doc in users:
            try:
                user_data = doc.to_dict()
                user_id = doc.id
                friends_list = user_data.get('friends', [])
                
                if not isinstance(friends_list, list) or len(friends_list) == 0:
                    continue
                
                for friend_id in friends_list:
                    if not friend_id or friend_id == user_id:
                        continue
                    
                    # Check if relationship already exists
                    existing = db.query(Friend).filter(
                        ((Friend.user_id == user_id) & (Friend.friend_id == friend_id)) |
                        ((Friend.user_id == friend_id) & (Friend.friend_id == user_id))
                    ).first()
                    
                    if existing:
                        continue
                    
                    # Create bidirectional friend relationship
                    friend1 = Friend(
                        user_id=user_id,
                        friend_id=friend_id,
                        status=FriendStatus.ACCEPTED.value,
                        created_at=datetime.now(),
                    )
                    friend2 = Friend(
                        user_id=friend_id,
                        friend_id=user_id,
                        status=FriendStatus.ACCEPTED.value,
                        created_at=datetime.now(),
                    )
                    db.add(friend1)
                    db.add(friend2)
                    stats["migrated"] += 1
                
                if stats["migrated"] % 10 == 0:
                    db.commit()
                
            except Exception as e:
                logger.error(f"Error migrating friends for user {doc.id}: {e}")
                stats["errors"] += 1
                db.rollback()
                continue
        
        db.commit()
        logger.info(f"Friends migration complete: {stats['migrated']} migrated, {stats['skipped']} skipped, {stats['errors']} errors")
        
    except Exception as e:
        logger.error(f"Error in friends migration: {e}")
        db.rollback()
        stats["errors"] += 1
    
    return stats


def main():
    """Main migration function"""
    logger.info("=" * 60)
    logger.info("Firestore to PostgreSQL Migration Script")
    logger.info("=" * 60)
    
    # Initialize Firestore
    firestore_db = init_firestore()
    if not firestore_db:
        logger.error("Failed to initialize Firestore. Exiting.")
        sys.exit(1)
    
    # Initialize database
    logger.info(f"Database URL: {settings.database_url}")
    init_db()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Run migrations
        total_stats = {
            "posts": {"migrated": 0, "skipped": 0, "errors": 0},
            "friends": {"migrated": 0, "skipped": 0, "errors": 0},
        }
        
        # Migrate posts
        post_stats = migrate_posts(db, firestore_db)
        total_stats["posts"] = post_stats
        
        # Migrate friends
        friend_stats = migrate_friends(db, firestore_db)
        total_stats["friends"] = friend_stats
        
        # Print summary
        logger.info("=" * 60)
        logger.info("MIGRATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Posts: {total_stats['posts']['migrated']} migrated, {total_stats['posts']['skipped']} skipped, {total_stats['posts']['errors']} errors")
        logger.info(f"Friends: {total_stats['friends']['migrated']} migrated, {total_stats['friends']['skipped']} skipped, {total_stats['friends']['errors']} errors")
        logger.info("=" * 60)
        logger.info("Migration complete!")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

