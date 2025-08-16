import os
import json
import toml
import streamlit as st
from firebase_admin import credentials

def get_firebase_creds():
    creds_json_str = os.environ.get("FIREBASE_CREDENTIALS_JSON")
    if creds_json_str:
        return credentials.Certificate(json.loads(creds_json_str))
    
    # Fallback to secrets.toml if running locally
    try:
        return credentials.Certificate(st.secrets["firebase"]["service_account"])
    except (KeyError, FileNotFoundError):
        # Fallback to local file if secrets don't work
        if os.path.exists("firebase-credentials.json"):
            return credentials.Certificate("firebase-credentials.json")
        else:
            st.error("Firebase credentials not found.")
            st.stop()

def load_api_keys():
    """Loads API keys from Streamlit secrets and sets them as environment variables."""
    try:
        if os.path.exists(".streamlit/secrets.toml"):
            secrets = toml.load(".streamlit/secrets.toml")
            for key, value in secrets.get("secrets", {}).items():
                os.environ[key] = str(value) # Ensure value is a string
    except Exception as e:
        st.error(f"Error loading API keys from secrets.toml: {e}")

def _load_user_prefs():
    """Loads user preferences from a local JSON file."""
    if os.path.exists("user_prefs.json"):
        with open("user_prefs.json", "r") as f:
            return json.load(f)
    return {}

def _save_user_prefs(prefs):
    """Saves user preferences to a local JSON file."""
    with open("user_prefs.json", "w") as f:
        json.dump(prefs, f, indent=4)
