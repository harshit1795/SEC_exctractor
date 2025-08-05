
import os
import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore

# --- Firebase Initialization ---

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

# --- User Authentication (OAuth) ---

def verify_id_token(id_token):
    """Verify the ID token and get the user's UID."""
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        st.session_state["user"] = uid
        st.session_state["logged_in"] = True
        
        # Check if user has a preferences document, if not create one
        doc_ref = db.collection("user_prefs").document(uid)
        if not doc_ref.get().exists:
            doc_ref.set({})
            
        return uid
    except auth.InvalidIdTokenError:
        st.error("Invalid ID token. Please try signing in again.")
        st.session_state["logged_in"] = False
        return None
    except Exception as e:
        st.error(f"Error during token verification: {e}")
        st.session_state["logged_in"] = False
        return None

# --- User Preferences (Firestore) ---

def _load_user_prefs() -> dict:
    """Load user preferences from Firestore."""
    if "user" not in st.session_state:
        return {}
        
    user_uid = st.session_state["user"]
    doc_ref = db.collection("user_prefs").document(user_uid)
    doc = doc_ref.get()
    
    if doc.exists:
        return doc.to_dict()
    return {}

def _save_user_prefs(prefs: dict):
    """Save user preferences to Firestore."""
    if "user" not in st.session_state:
        return
        
    user_uid = st.session_state["user"]
    doc_ref = db.collection("user_prefs").document(user_uid)
    doc_ref.set(prefs)

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

# --- Nexus Community Feed (Firestore) ---

def load_nexus_feed() -> list:
    """Load the Nexus community feed from Firestore."""
    doc_ref = db.collection("nexus_data").document("feed")
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict().get("items", [])
    return []

def save_nexus_feed(feed_data: list):
    """Save the Nexus community feed to Firestore."""
    doc_ref = db.collection("nexus_data").document("feed")
    doc_ref.set({"items": feed_.items})
