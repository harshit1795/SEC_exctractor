import streamlit as st
import firebase_admin
from firebase_admin import auth

def hide_default_sidebar():
    st.markdown("""
        <style>
            div[data-testid="stSidebarNav"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Renders the sidebar navigation."""
    with st.sidebar:
        st.image("FInQLogo.png", width=100)
        st.title("FinQ Modules")

        page = st.radio(
            "Navigation",
            options=["Dashboard", "Financial Health Monitoring", "Nexus", "Settings"],
            key="navigation_main"
        )

        if st.button("Log Out"):
            if st.session_state.get("user"):
                try:
                    auth.revoke_refresh_tokens(st.session_state["user"])
                except Exception as e:
                    st.error(f"Error logging out: {e}")
            st.session_state["logged_in"] = False
            st.session_state["user"] = None
            st.rerun()
    
    return page