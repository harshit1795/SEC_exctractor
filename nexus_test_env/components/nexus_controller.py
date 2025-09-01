from components.nexus_database import NexusDatabase
from components.nexus_models import UserProfile, UserConnections, Post, Comment, Message
import uuid
from datetime import datetime
from typing import Optional, List

class NexusController:
    def __init__(self, agent=None):
        self.db = NexusDatabase()
        self.agent = agent

    # --- User Management ---
    def get_or_create_user_profile(self, uid: str, display_name: str = "") -> Optional[UserProfile]:
        profile = self.db.get_user_profile(uid)
        if profile:
            return profile
        
        new_profile = UserProfile(uid=uid, display_name=display_name or uid)
        if self.db.create_or_update_user_profile(new_profile):
            return new_profile
        return None

    def update_user_profile(self, profile: UserProfile) -> bool:
        profile.updated_at = datetime.utcnow()
        return self.db.create_or_update_user_profile(profile)

    # --- Social Features ---
    def send_friend_request(self, from_uid: str, to_uid: str) -> bool:
        connections = self.db.get_user_connections(to_uid) or UserConnections(uid=to_uid)
        if from_uid not in connections.requests:
            connections.requests.append(from_uid)
            return self.db.create_or_update_user_connections(connections)
        return True

    def accept_friend_request(self, user_uid: str, requester_uid: str) -> bool:
        # Add to user's friends
        user_connections = self.db.get_user_connections(user_uid) or UserConnections(uid=user_uid)
        if requester_uid in user_connections.requests:
            user_connections.requests.remove(requester_uid)
            if requester_uid not in user_connections.friends:
                user_connections.friends.append(requester_uid)
            self.db.create_or_update_user_connections(user_connections)

        # Add to requester's friends
        requester_connections = self.db.get_user_connections(requester_uid) or UserConnections(uid=requester_uid)
        if user_uid not in requester_connections.friends:
            requester_connections.friends.append(user_uid)
        self.db.create_or_update_user_connections(requester_connections)
        return True

    def remove_friend(self, user1_uid: str, user2_uid: str) -> bool:
        # Remove from user1's friends
        user1_connections = self.db.get_user_connections(user1_uid)
        if user1_connections and user2_uid in user1_connections.friends:
            user1_connections.friends.remove(user2_uid)
            self.db.create_or_update_user_connections(user1_connections)

        # Remove from user2's friends
        user2_connections = self.db.get_user_connections(user2_uid)
        if user2_connections and user1_uid in user2_connections.friends:
            user2_connections.friends.remove(user1_uid)
            self.db.create_or_update_user_connections(user2_connections)
        return True

    # --- Content Management ---
    def create_post(self, author_id: str, content: str, **kwargs) -> Optional[Post]:
        post_id = str(uuid.uuid4())
        post = Post(id=post_id, author_id=author_id, content=content, **kwargs)
        if self.db.create_post(post):
            return post
        return None

    def like_post(self, user_id: str, post_id: str) -> bool:
        post = self.db.get_post(post_id)
        if post:
            if user_id not in post.likes:
                post.likes.append(user_id)
            else:
                post.likes.remove(user_id)
            return self.db.create_post(post)
        return False

    def create_comment(self, author_id: str, post_id: str, text: str) -> Optional[Comment]:
        comment_id = str(uuid.uuid4())
        comment = Comment(id=comment_id, author_id=author_id, post_id=post_id, text=text)
        if self.db.create_comment(comment):
            return comment
        return None

    # --- Messaging ---
    def send_message(self, from_user: str, to_user: str, text: str) -> Optional[Message]:
        message_id = str(uuid.uuid4())
        message = Message(id=message_id, from_user=from_user, to_user=to_user, text=text)
        if self.db.create_message(message):
            return message
        return None

    def get_user_list(self) -> List[UserProfile]:
        try:
            docs = self.db.db.collection("nexus_profiles").stream()
            return [UserProfile(**doc.to_dict()) for doc in docs]
        except Exception as e:
            print(f"Error getting user list: {e}")
            return []
