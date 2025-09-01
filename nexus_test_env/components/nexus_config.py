import streamlit as st
import firebase_admin
from firebase_admin import credentials
import os

def initialize_firebase():
    """Initializes the Firebase Admin SDK using a credentials.json file."""
    if firebase_admin._apps:
        return True

    creds_path = "firebase_credentials.json" 

    if not os.path.exists(creds_path):
        st.error(f"Firebase credentials file not found at {creds_path}. Please place the file in the root of the test environment.")
        return False

    try:
        creds = credentials.Certificate(creds_path)
        firebase_admin.initialize_app(creds)
        return True
    except Exception as e:
        st.error(f"Failed to initialize Firebase from {creds_path}: {e}")
        return False

def get_nexus_settings():
    """Returns application settings for Nexus."""
    return {
        "max_posts_per_user": 1000,
        "max_messages_per_conversation": 1000,
        "max_comments_per_post": 500,
        "max_profile_picture_size_mb": 5,
        "post_char_limit": 2000,
    }
