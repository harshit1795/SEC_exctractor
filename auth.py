
import os
import json
import streamlit as st

PREFS_PATH = "user_prefs.json"

def _load_user_prefs() -> dict:
    if os.path.exists(PREFS_PATH):
        try:
            with open(PREFS_PATH, "r") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return {}
    return {}

def _save_user_prefs(prefs: dict):
    try:
        with open(PREFS_PATH, "w") as f:
            json.dump(prefs, f, indent=2)
    except Exception:
        pass

def load_api_keys():
    """Load API keys from user preferences or settoken.sh and configure services."""
    user = st.session_state.get("user", "default")
    all_prefs = _load_user_prefs()
    user_prefs = all_prefs.get(user, {})

    # Load from user preferences first
    gemini_key = user_prefs.get("GEMINI_API_KEY")
    fred_key = user_prefs.get("FRED_API_KEY")

    # Fallback to settoken.sh if not in user prefs
    if not gemini_key or not fred_key:
        try:
            with open("settoken.sh", 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('export') and '=' in line:
                        key, value = line.replace('export ', '').split('=', 1)
                        value = value.strip('"')
                        if key == "GEMINI_API_KEY" and not gemini_key:
                            gemini_key = value
                        elif key == "FRED_API_KEY" and not fred_key:
                            fred_key = value
        except FileNotFoundError:
            pass # It's okay if the file doesn't exist

    # Set environment variables for other modules to use
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key
    if fred_key:
        os.environ["FRED_API_KEY"] = fred_key

    # Configure Gemini
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
