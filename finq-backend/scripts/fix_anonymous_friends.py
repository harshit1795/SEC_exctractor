"""
Script to fix friends that were created with 'anonymous' as user_id
This migrates anonymous friendships to actual user IDs based on user profiles
"""
from app.database import SessionLocal
from app.models.friend import Friend, FriendStatus
from app.models.user_profile import UserProfile
import sys

def fix_anonymous_friends():
    db = SessionLocal()
    
    try:
        # Find all friends with 'anonymous'
        anonymous_friends = db.query(Friend).filter(
            (Friend.user_id == 'anonymous') | (Friend.friend_id == 'anonymous'),
            Friend.status == FriendStatus.ACCEPTED.value
        ).all()
        
        print(f"Found {len(anonymous_friends)} friendships with 'anonymous'")
        
        # Get all user profiles to map display names to user IDs
        profiles = {p.user_id: p for p in db.query(UserProfile).all()}
        
        fixed_count = 0
        for f in anonymous_friends:
            # Determine which side is anonymous and which is the real user
            if f.user_id == 'anonymous':
                # The friend_id is the real user
                real_user_id = f.friend_id
                # We need to find who the anonymous user actually is
                # This is tricky - we'll need user input or logic to determine
                print(f"  Found: anonymous -> {real_user_id} (status: {f.status})")
                print(f"    Need to determine who 'anonymous' should be")
            elif f.friend_id == 'anonymous':
                # The user_id is the real user
                real_user_id = f.user_id
                print(f"  Found: {real_user_id} -> anonymous (status: {f.status})")
                print(f"    Need to determine who 'anonymous' should be")
        
        print(f"\nNote: This script identifies the issue but cannot automatically fix it")
        print(f"because we don't know which user was logged in as 'anonymous'.")
        print(f"\nTo fix manually:")
        print(f"1. Identify the actual user ID for each 'anonymous' friendship")
        print(f"2. Update the friend records in the database")
        print(f"\nExample SQL:")
        print(f"UPDATE friends SET user_id = 'ACTUAL_USER_ID' WHERE user_id = 'anonymous' AND friend_id = 'KNOWN_FRIEND_ID';")
        print(f"UPDATE friends SET friend_id = 'ACTUAL_USER_ID' WHERE friend_id = 'anonymous' AND user_id = 'KNOWN_USER_ID';")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_anonymous_friends()

