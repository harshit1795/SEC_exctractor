"""
Firebase helper functions for the Nexus module.
"""

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

def get_db():
    """Returns an initialized Firestore client."""
    if not firebase_admin._apps:
        # This is a fallback, the app should be initialized in login.py
        try:
            creds = credentials.Certificate(st.secrets["firebase_credentials"])
            firebase_admin.initialize_app(creds)
        except Exception as e:
            st.error(f"Could not initialize Firebase: {e}")
            return None
    return firestore.client()

def get_user_profile(user_id):
    """Fetches a user profile from Firestore."""
    db = get_db()
    if not db:
        return None
    try:
        doc_ref = db.collection('users').document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            return None
    except Exception as e:
        st.error(f"Error getting user profile: {e}")
        return None

def update_user_profile(user_id, data):
    """Updates a user profile in Firestore."""
    db = get_db()
    if not db:
        st.error("Firestore database not initialized.")
        return False
    try:
        doc_ref = db.collection('users').document(user_id)
        doc_ref.set(data, merge=True)
        return True
    except Exception as e:
        st.error(f"Error updating user profile: {e}")
        print(e)
        return False

def get_all_users():
    """Fetches all users from Firestore."""
    db = get_db()
    if not db:
        return []
    try:
        users_ref = db.collection('users')
        users = []
        for doc in users_ref.stream():
            user_data = doc.to_dict()
            user_data['uid'] = doc.id
            users.append(user_data)
        return users
    except Exception as e:
        st.error(f"Error getting all users: {e}")
        return []

def send_friend_request(from_user_id, to_user_id):
    """Sends a friend request."""
    db = get_db()
    if not db:
        return False
    try:
        # Check if a request already exists
        requests_ref = db.collection('friend_requests')
        existing_request = requests_ref.where('fromUserId', '==', from_user_id).where('toUserId', '==', to_user_id).get()
        if len(existing_request) > 0:
            st.warning("Friend request already sent.")
            return False

        requests_ref.add({
            'fromUserId': from_user_id,
            'toUserId': to_user_id,
            'status': 'pending'
        })
        return True
    except Exception as e:
        st.error(f"Error sending friend request: {e}")
        return False

def get_friend_requests(user_id):
    """Fetches pending friend requests for a user."""
    db = get_db()
    if not db:
        return []
    try:
        requests_ref = db.collection('friend_requests')
        requests = []
        for doc in requests_ref.where('toUserId', '==', user_id).where('status', '==', 'pending').stream():
            request_data = doc.to_dict()
            request_data['id'] = doc.id
            requests.append(request_data)
        return requests
    except Exception as e:
        st.error(f"Error getting friend requests: {e}")
        return []

@firestore.transactional
def accept_friend_request_transaction(transaction, from_user_ref, to_user_ref, request_ref):
    from_user_snapshot = from_user_ref.get(transaction=transaction)
    to_user_snapshot = to_user_ref.get(transaction=transaction)

    # Add to friends lists
    transaction.update(from_user_ref, {'friends': firestore.ArrayUnion([to_user_snapshot.id])})
    transaction.update(to_user_ref, {'friends': firestore.ArrayUnion([from_user_snapshot.id])})

    # Update request status
    transaction.update(request_ref, {'status': 'accepted'})

def accept_friend_request(request_id, from_user_id, to_user_id):
    """Accepts a friend request."""
    db = get_db()
    if not db:
        return False
    try:
        transaction = db.transaction()
        from_user_ref = db.collection('users').document(from_user_id)
        to_user_ref = db.collection('users').document(to_user_id)
        request_ref = db.collection('friend_requests').document(request_id)
        accept_friend_request_transaction(transaction, from_user_ref, to_user_ref, request_ref)
        return True
    except Exception as e:
        st.error(f"Error accepting friend request: {e}")
        return False

def reject_friend_request(request_id):
    """Rejects a friend request."""
    db = get_db()
    if not db:
        return False
    try:
        request_ref = db.collection('friend_requests').document(request_id)
        request_ref.update({'status': 'rejected'})
        return True
    except Exception as e:
        st.error(f"Error rejecting friend request: {e}")
        return False

def get_friends(user_id):
    """Fetches a user's friends."""
    db = get_db()
    if not db:
        return []
    try:
        user_profile = get_user_profile(user_id)
        if not user_profile or 'friends' not in user_profile:
            return []
        
        friend_ids = user_profile['friends']
        friends = []
        for friend_id in friend_ids:
            friend_profile = get_user_profile(friend_id)
            if friend_profile:
                friend_profile['uid'] = friend_id
                friends.append(friend_profile)
        return friends
    except Exception as e:
        st.error(f"Error getting friends: {e}")
        return []

def create_post(author_id, content):
    """Creates a new post in Firestore."""
    db = get_db()
    if not db:
        return False
    try:
        posts_ref = db.collection('posts')
        posts_ref.add({
            'authorId': author_id,
            'content': content,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'likes': [],
            'comments': []
        })
        return True
    except Exception as e:
        st.error(f"Error creating post: {e}")
        return False

def get_friends_posts(user_id):
    """Fetches posts from a user's friends."""
    db = get_db()
    if not db:
        return []
    try:
        user_profile = get_user_profile(user_id)
        if not user_profile or 'friends' not in user_profile:
            return []
        
        friend_ids = user_profile['friends']
        if not friend_ids:
            return []

        posts_ref = db.collection('posts')
        query = posts_ref.where('authorId', 'in', friend_ids).order_by('timestamp', direction=firestore.Query.DESCENDING)
        
        posts = []
        for doc in query.stream():
            post_data = doc.to_dict()
            post_data['id'] = doc.id
            posts.append(post_data)
        return posts
    except Exception as e:
        st.error(f"Error getting friends posts: {e}")
        return []

def get_user_posts(user_id):
    """Fetches all posts by a specific user."""
    db = get_db()
    if not db:
        return []
    try:
        posts_ref = db.collection('posts')
        query = posts_ref.where('authorId', '==', user_id).order_by('timestamp', direction=firestore.Query.DESCENDING)
        
        posts = []
        for doc in query.stream():
            post_data = doc.to_dict()
            post_data['id'] = doc.id
            posts.append(post_data)
        return posts
    except Exception as e:
        st.error(f"Error getting user posts: {e}")
        return []

def update_post(post_id, new_content):
    """Updates a post in Firestore."""
    db = get_db()
    if not db:
        return False
    try:
        post_ref = db.collection('posts').document(post_id)
        post_ref.update({
            'content': new_content,
            'lastEdited': firestore.SERVER_TIMESTAMP
        })
        return True
    except Exception as e:
        st.error(f"Error updating post: {e}")
        return False

def delete_post(post_id):
    """Deletes a post from Firestore."""
    db = get_db()
    if not db:
        return False
    try:
        post_ref = db.collection('posts').document(post_id)
        post_ref.delete()
        return True
    except Exception as e:
        st.error(f"Error deleting post: {e}")
        return False

def remove_friend(user_id, friend_id):
    """Removes a friend from both users' friend lists."""
    db = get_db()
    if not db:
        return False
    try:
        user_ref = db.collection('users').document(user_id)
        friend_ref = db.collection('users').document(friend_id)

        user_ref.update({'friends': firestore.ArrayRemove([friend_id])})
        friend_ref.update({'friends': firestore.ArrayRemove([user_id])})
        
        return True
    except Exception as e:
        st.error(f"Error removing friend: {e}")
        return False

def get_outgoing_friend_requests(user_id):
    """Fetches pending friend requests sent by a user."""
    db = get_db()
    if not db:
        return []
    try:
        requests_ref = db.collection('friend_requests')
        requests = []
        for doc in requests_ref.where('fromUserId', '==', user_id).where('status', '==', 'pending').stream():
            request_data = doc.to_dict()
            request_data['id'] = doc.id
            requests.append(request_data)
        return requests
    except Exception as e:
        st.error(f"Error getting outgoing friend requests: {e}")
        return []

def cancel_friend_request(request_id):
    """Cancels a friend request by deleting the request document."""
    db = get_db()
    if not db:
        return False
    try:
        request_ref = db.collection('friend_requests').document(request_id)
        request_ref.delete()
        return True
    except Exception as e:
        st.error(f"Error cancelling friend request: {e}")
        return False

def like_post(post_id, user_id):
    """Adds a user's ID to the likes array of a post."""
    db = get_db()
    if not db:
        return False
    try:
        post_ref = db.collection('posts').document(post_id)
        post_ref.update({'likes': firestore.ArrayUnion([user_id])})
        return True
    except Exception as e:
        st.error(f"Error liking post: {e}")
        return False

def unlike_post(post_id, user_id):
    """Removes a user's ID from the likes array of a post."""
    db = get_db()
    if not db:
        return False
    try:
        post_ref = db.collection('posts').document(post_id)
        post_ref.update({'likes': firestore.ArrayRemove([user_id])})
        return True
    except Exception as e:
        st.error(f"Error unliking post: {e}")
        return False

def add_comment(post_id, user_id, comment_text):
    """Adds a comment to a post."""
    db = get_db()
    if not db:
        return False
    try:
        post_ref = db.collection('posts').document(post_id)
        comment = {
            'userId': user_id,
            'text': comment_text,
            'timestamp': firestore.SERVER_TIMESTAMP
        }
        post_ref.update({'comments': firestore.ArrayUnion([comment])})
        return True
    except Exception as e:
        st.error(f"Error adding comment: {e}")
        return False
