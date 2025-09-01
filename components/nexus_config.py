import streamlit as st
import firebase_admin
from firebase_admin import credentials
import os

def initialize_firebase():
    """Initializes the Firebase Admin SDK using credentials from Streamlit secrets or environment variables."""
    if firebase_admin._apps:
        return True

    try:
        # Try to get credentials from Streamlit secrets first
        creds_json = st.secrets.get("firebase")
        if creds_json:
            creds = credentials.Certificate(creds_json)
        else:
            # Fallback to environment variables for local development
            creds_dict = {
                "type": os.environ.get("FIREBASE_TYPE"),
                "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
                "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.environ.get("FIREBASE_PRIVATE_KEY", "").replace('\n', '\n'),
                "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
                "auth_uri": os.environ.get("FIREBASE_AUTH_URI"),
                "token_uri": os.environ.get("FIREBASE_TOKEN_URI"),
                "auth_provider_x509_cert_url": os.environ.get("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
                "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_X509_CERT_URL"),
            }
            if not all(creds_dict.values()):
                st.error("Firebase credentials not found. Please set them in Streamlit secrets or environment variables.")
                return False
            creds = credentials.Certificate(cres_dict)

        firebase_admin.initialize_app(creds)
        return True
    except Exception as e:
        st.error(f"Failed to initialize Firebase: {e}")
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
