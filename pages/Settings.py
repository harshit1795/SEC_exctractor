import streamlit as st
from auth import _load_user_prefs, _save_user_prefs

def render():
    st.markdown("<h2 style='text-align: center;'>⚙️ Settings</h2>", unsafe_allow_html=True)

    st.subheader("API Keys")

    # Get user preferences
    user_prefs = _load_user_prefs().get(st.session_state.get("user"), {})

    # Gemini API Key
    gemini_api_key = st.text_input("Gemini API Key", value=user_prefs.get("GEMINI_API_KEY", ""), type="password")
    if st.button("Save Gemini Key"):
        all_prefs = _load_user_prefs()
        user = st.session_state.get("user")
        if user:
            all_prefs.setdefault(user, {})["GEMINI_API_KEY"] = gemini_api_key
            _save_user_prefs(all_prefs)
            st.success("Gemini API Key saved!")

    # FRED API Key
    fred_api_key = st.text_input("FRED API Key", value=user_prefs.get("FRED_API_KEY", ""), type="password")
    if st.button("Save FRED Key"):
        all_prefs = _load_user_prefs()
        user = st.session_state.get("user")
        if user:
            all_prefs.setdefault(user, {})["FRED_API_KEY"] = fred_api_key
            _save_user_prefs(all_prefs)
            st.success("FRED API Key saved!")
