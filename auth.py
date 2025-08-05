
import os
import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
from google.cloud import storage

# --- Firebase & Google Cloud Initialization ---

# Check if Firebase app is already initialized
if not firebase_admin._apps:
    try:
        # Try to use credentials from Streamlit secrets first
        cred = credentials.Certificate(st.secrets["firebase_credentials"])
    except (KeyError, FileNotFoundError):
        # Fallback to a local file for development
        if os.path.exists("firebase-credentials.json"):
            cred = credentials.Certificate("firebase-credentials.json")
        else:
            st.error("Firebase credentials not found. Please add them to your Streamlit secrets or create a 'firebase-credentials.json' file.")
            st.stop()
    
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- User Authentication ---

def create_user(email, password):
    """Create a new user in Firebase Authentication."""
    try:
        user = auth.create_user(email=email, password=password)
        st.success(f"Successfully created user: {user.uid}")
        return user
    except Exception as e:
        st.error(f"Error creating user: {e}")
        return None

def login_user(email, password):
    """Login a user with email and password."""
    try:
        # This is a simplified example. In a real app, you'd handle this securely.
        # Firebase Admin SDK doesn't directly handle password verification.
        # This is typically done on the client-side with the Firebase Auth client SDK.
        # For this backend-only example, we'll assume a custom token approach or similar.
        # A simple placeholder for the login logic:
        user = auth.get_user_by_email(email)
        st.session_state["user"] = user.uid
        st.session_state["logged_in"] = True
        return user
    except Exception as e:
        st.error(f"Error logging in: {e}")
        st.session_state["logged_in"] = False
        return None

def reset_password(email):
    """Send a password reset email."""
    try:
        link = auth.generate_password_reset_link(email)
        st.success(f"Password reset link sent to {email}")
        # You would typically email this link to the user.
        print(f"Password reset link: {link}")
    except Exception as e:
        st.error(f"Error sending password reset email: {e}")

# --- User Preferences (Cloud Storage) ---

BUCKET_NAME = "REPLACE_WITH_YOUR_BUCKET_NAME"  # <-- IMPORTANT: Replace with your bucket name

def _get_user_prefs_blob():
    """Get the GCS blob for the current user's preferences."""
    if "user" not in st.session_state:
        return None
    
    if BUCKET_NAME == "REPLACE_WITH_YOUR_BUCKET_NAME":
        st.error("Google Cloud Storage bucket name is not configured. Please update it in `auth.py`.")
        st.stop()
        
    user_uid = st.session_state["user"]
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    return bucket.blob(f"user_prefs/{user_uid}.json")

def _load_user_prefs() -> dict:
    """Load user preferences from Google Cloud Storage."""
    blob = _get_user_prefs_blob()
    if blob and blob.exists():
        try:
            return json.loads(blob.download_as_string())
        except (IOError, json.JSONDecodeError):
            return {}
    return {}

def _save_user_prefs(prefs: dict):
    """Save user preferences to Google Cloud Storage."""
    blob = _get_user_prefs_blob()
    if blob:
        try:
            blob.upload_from_string(
                json.dumps(prefs, indent=2),
                content_type="application/json"
            )
        except Exception as e:
            st.error(f"Failed to save user preferences: {e}")

# --- API Key Management ---

def load_api_keys():
    """Load API keys from user preferences and configure services."""
    if "user" not in st.session_state:
        return False

    user_prefs = _load_user_prefs()
    gemini_key = user_prefs.get("GEMINI_API_KEY")
    fred_key = user_prefs.get("FRED_API_KEY")

    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key
    if fred_key:
        os.environ["FRED_API_KEY"] = fred_key

    if os.environ.get("GEMINI_API_KEY"):
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.environ["GEMINI_API_KEY"])
            return True
        except Exception as e:
            st.error(f"Failed to configure Gemini: {e}")
            return False
    else:
        st.warning("GEMINI_API_KEY is not set. Please add it in the Settings page.")
        return False

# --- Nexus Community Feed (Cloud Storage) ---

NEXUS_FEED_BLOB = "nexus_feed/feed.json"

def load_nexus_feed():
    """Load the Nexus community feed from Google Cloud Storage."""
    if BUCKET_NAME == "REPLACE_WITH_YOUR_BUCKET_NAME":
        st.error("Google Cloud Storage bucket name is not configured. Please update it in `auth.py`.")
        st.stop()
        
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NEXUS_FEED_BLOB)
    blob = bucket.blob(NEXUS_FEED_BLOB)
    if blob.exists():
        try:
            return json.loads(blob.download_as_string())
        except (IOError, json.JSONDecodeError):
            return []
    return []

def save_nexus_feed(feed_data):
    """Save the Nexus community feed to Google Cloud Storage."""
    if BUCKET_NAME == "REPLACE_WITH_YOUR_BUCKET_NAME":
        st.error("Google Cloud Storage bucket name is not configured. Please update it in `auth.py`.")
        st.stop()
        
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(NEXUS_FEED_BLOB)
    try:
        blob.upload_from_string(
            json.dumps(feed_data, indent=2),
            content_type="application/json"
        )
    except Exception as e:
        st.error(f"Failed to save Nexus feed: {e}")
