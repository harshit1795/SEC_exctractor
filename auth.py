import os
import json
import streamlit as st
import logging
import firebase_admin
from firebase_admin import credentials, auth, firestore

# --- Firebase Initialization ---
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(st.secrets["firebase_credentials"])
    except (KeyError, FileNotFoundError):
        if os.path.exists("firebase-credentials.json"):
            cred = credentials.Certificate("firebase-credentials.json")
        else:
            st.error("Firebase credentials not found.")
            st.stop()
    firebase_admin.initialize_app(cred)

db = firestore.client()

logger = logging.getLogger(__name__)

# --- User Authentication ---

def verify_google_token(id_token):
    """Verify Google ID token and return user info."""
    try:
        logger.info("Verifying Google ID token.")
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token.get('uid')
        logger.info("ID token verified successfully for uid: %s", uid)
        # Check if user exists in Firestore, if not, create a new record
        user_ref = db.collection("user_prefs").document(uid)
        if not user_ref.get().exists:
            logger.info("Creating new Firestore record for uid: %s", uid)
            user_ref.set({})
        return decoded_token
    except Exception as e:
        logger.error("Error verifying Google token: %s", e)
        st.error(f"Error verifying Google token: {e}")
        return None

def create_user(email, password):
    """Create a new user in Firebase Authentication."""
    try:
        user = auth.create_user(email=email, password=password)
        st.success(f"Successfully created user: {user.uid}")
        db.collection("user_prefs").document(user.uid).set({})
        return user
    except Exception as e:
        st.error(f"Error creating user: {e}")
        return None

def login_user(email=None, password=None, id_token=None):
    """Login a user with email/password or Google ID token."""
    if id_token:
        decoded_token = verify_google_token(id_token)
        if decoded_token:
            st.session_state["user"] = decoded_token['uid']
            st.session_state["logged_in"] = True
            return decoded_token
    elif email and password:
        try:
            user = auth.get_user_by_email(email)
            st.session_state["user"] = user.uid
            st.session_state["logged_in"] = True
            return user
        except Exception as e:
            st.error(f"Error logging in: {e}")
            st.session_state["logged_in"] = False
            return None
    return None

def reset_password(email):
    """Send a password reset email."""
    try:
        link = auth.generate_password_reset_link(email)
        st.success(f"Password reset link sent to {email}")
        print(f"Password reset link: {link}")
    except Exception as e:
        st.error(f"Error sending password reset email: {e}")

# --- User Preferences (Firestore) ---
def _load_user_prefs() -> dict:
    if "user" not in st.session_state:
        return {}
    user_uid = st.session_state["user"]
    doc_ref = db.collection("user_prefs").document(user_uid)
    doc = doc_ref.get()
    return doc.to_dict() if doc.exists else {}

def _save_user_prefs(prefs: dict):
    if "user" not in st.session_state:
        return
    user_uid = st.session_state["user"]
    doc_ref = db.collection("user_prefs").document(user_uid)
    doc_ref.set(prefs)

# --- API Key Management ---
def load_api_keys():
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

# --- Nexus Community Feed (Firestore) ---
def load_nexus_feed() -> list:
    doc_ref = db.collection("nexus_data").document("feed")
    doc = doc_ref.get()
    return doc.to_dict().get("items", []) if doc.exists else []

def save_nexus_feed(feed_data: list):
    doc_ref = db.collection("nexus_data").document("feed")
    doc_ref.set({"items": feed_data})
