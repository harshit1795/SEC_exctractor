
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

# --- User Authentication ---

def create_user(email, password):
    """Create a new user in Firebase Authentication."""
    try:
        user = auth.create_user(email=email, password=password)
        st.success(f"Successfully created user: {user.uid}")
        # Create an empty preferences document for the new user
        db.collection("user_prefs").document(user.uid).set({})
        return user
    except Exception as e:
        st.error(f"Error creating user: {e}")
        return None

def login_user(email, password):
    """Login a user with email and password."""
    try:
        # This is a simplified example. In a real app, you'd handle this securely.
        user = auth.get_user_by_email(email)
        # Here you would typically verify the password using a client-side SDK and a custom token.
        # For this backend-only example, we are trusting the provided credentials.
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
    doc_ref.set({"items": feed_data})
