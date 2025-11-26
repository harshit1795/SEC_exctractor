"""
Script to clear all existing user data, friends, posts, and start fresh
This will reset the Nexus community to a clean state
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.friend import Friend
from app.models.post import Post, PostLike, PostComment
from app.models.user_profile import UserProfile
from app.models.insight import Insight

def clear_all_data():
    """Clear all user-related data from the database"""
    db = SessionLocal()
    
    try:
        print("Starting data cleanup...")
        
        # Count existing data
        friends_count = db.query(Friend).count()
        posts_count = db.query(Post).count()
        likes_count = db.query(PostLike).count()
        comments_count = db.query(PostComment).count()
        profiles_count = db.query(UserProfile).count()
        insights_count = db.query(Insight).count()
        
        print(f"\nCurrent data counts:")
        print(f"  Friends: {friends_count}")
        print(f"  Posts: {posts_count}")
        print(f"  Likes: {likes_count}")
        print(f"  Comments: {comments_count}")
        print(f"  User Profiles: {profiles_count}")
        print(f"  Insights: {insights_count}")
        
        # Confirm deletion
        response = input("\nAre you sure you want to delete ALL this data? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled. No data was deleted.")
            return
        
        print("\nDeleting data...")
        
        # Delete in order to respect foreign key constraints
        db.query(PostComment).delete()
        print(f"  ✓ Deleted {comments_count} comments")
        
        db.query(PostLike).delete()
        print(f"  ✓ Deleted {likes_count} likes")
        
        db.query(Post).delete()
        print(f"  ✓ Deleted {posts_count} posts")
        
        db.query(Friend).delete()
        print(f"  ✓ Deleted {friends_count} friends")
        
        db.query(Insight).delete()
        print(f"  ✓ Deleted {insights_count} insights")
        
        db.query(UserProfile).delete()
        print(f"  ✓ Deleted {profiles_count} user profiles")
        
        db.commit()
        
        print("\n✅ All data cleared successfully!")
        print("The database is now clean and ready for fresh users.")
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    clear_all_data()

