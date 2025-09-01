import firebase_admin
from firebase_admin import firestore
from typing import List, Optional
from components.nexus_models import UserProfile, UserConnections, Post, Comment, Message
from dataclasses import asdict

class NexusDatabase:
    def __init__(self):
        if not firebase_admin._apps:
            raise Exception("Firebase has not been initialized. Call initialize_firebase() first.")
        self.db = firestore.client()

    # --- UserProfile Methods ---
    def create_or_update_user_profile(self, profile: UserProfile) -> bool:
        try:
            self.db.collection("nexus_profiles").document(profile.uid).set(asdict(profile))
            return True
        except Exception as e:
            print(f"Error creating/updating user profile: {e}")
            return False

    def get_user_profile(self, uid: str) -> Optional[UserProfile]:
        try:
            doc = self.db.collection("nexus_profiles").document(uid).get()
            if doc.exists:
                return UserProfile(**doc.to_dict())
            return None
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None

    # --- UserConnections Methods ---
    def create_or_update_user_connections(self, connections: UserConnections) -> bool:
        try:
            self.db.collection("nexus_connections").document(connections.uid).set(asdict(connections))
            return True
        except Exception as e:
            print(f"Error creating/updating user connections: {e}")
            return False

    def get_user_connections(self, uid: str) -> Optional[UserConnections]:
        try:
            doc = self.db.collection("nexus_connections").document(uid).get()
            if doc.exists:
                return UserConnections(**doc.to_dict())
            return None
        except Exception as e:
            print(f"Error getting user connections: {e}")
            return None

    # --- Post Methods ---
    def create_post(self, post: Post) -> bool:
        try:
            self.db.collection("nexus_posts").document(post.id).set(asdict(post))
            return True
        except Exception as e:
            print(f"Error creating post: {e}")
            return False

    def get_post(self, post_id: str) -> Optional[Post]:
        try:
            doc = self.db.collection("nexus_posts").document(post_id).get()
            if doc.exists:
                return Post(**doc.to_dict())
            return None
        except Exception as e:
            print(f"Error getting post: {e}")
            return None

    def get_user_posts(self, author_id: str, limit: int = 50) -> List[Post]:
        try:
            docs = self.db.collection("nexus_posts").where("author_id", "==", author_id).order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit).stream()
            return [Post(**doc.to_dict()) for doc in docs]
        except Exception as e:
            print(f"Error getting user posts: {e}")
            return []

    # --- Comment Methods ---
    def create_comment(self, comment: Comment) -> bool:
        try:
            self.db.collection("nexus_comments").document(comment.id).set(asdict(comment))
            return True
        except Exception as e:
            print(f"Error creating comment: {e}")
            return False

    def get_post_comments(self, post_id: str, limit: int = 100) -> List[Comment]:
        try:
            docs = self.db.collection("nexus_comments").where("post_id", "==", post_id).order_by("created_at", direction=firestore.Query.ASCENDING).limit(limit).stream()
            return [Comment(**doc.to_dict()) for doc in docs]
        except Exception as e:
            print(f"Error getting post comments: {e}")
            return []

    # --- Message Methods ---
    def create_message(self, message: Message) -> bool:
        try:
            self.db.collection("nexus_messages").document(message.id).set(asdict(message))
            return True
        except Exception as e:
            print(f"Error creating message: {e}")
            return False

    def get_conversation(self, user1_id: str, user2_id: str, limit: int = 100) -> List[Message]:
        try:
            messages = []
            q1 = self.db.collection("nexus_messages").where("from_user", "==", user1_id).where("to_user", "==", user2_id)
            q2 = self.db.collection("nexus_messages").where("from_user", "==", user2_id).where("to_user", "==", user1_id)
            
            docs1 = q1.stream()
            docs2 = q2.stream()

            for doc in docs1:
                messages.append(Message(**doc.to_dict()))
            for doc in docs2:
                messages.append(Message(**doc.to_dict()))

            messages.sort(key=lambda x: x.created_at)
            return messages[-limit:]
        except Exception as e:
            print(f"Error getting conversation: {e}")
            return []
