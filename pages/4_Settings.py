
import streamlit as st
from auth import _load_user_prefs, _save_user_prefs

st.set_page_config(page_title="Settings - FinQ", page_icon="⚙️")

st.title("Settings")

# --- API Key Management ---
st.header("API Key Configuration")

# Load existing preferences
user_prefs = _load_user_prefs()
gemini_api_key = st.text_input("Gemini API Key", value=user_prefs.get("GEMINI_API_KEY", ""), type="password")
fred_api_key = st.text_input("FRED API Key", value=user_prefs.get("FRED_API_KEY", ""), type="password")

if st.button("Save API Keys"):
    user_prefs["GEMINI_API_KEY"] = gemini_api_key
    user_prefs["FRED_API_KEY"] = fred_api_key
    _save_user_prefs(user_prefs)
    st.success("API Keys saved successfully!")

# --- Back to Main App ---
if st.button("Back to Dashboard"):
    st.switch_page("Home.py")
