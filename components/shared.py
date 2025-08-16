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

        PAGES = {
            "Dashboard": "fa-chart-pie",
            "Financial Health Monitoring": "fa-heart-pulse",
            "Nexus": "fa-cubes",
            "Settings": "fa-gear",
        }

        if 'active_page' not in st.session_state:
            st.session_state.active_page = "Dashboard"

        for page, icon in PAGES.items():
            is_active = (page == st.session_state.active_page)
            st.markdown(f'<div style="text-align: center;"><i class="fa-solid {icon}"></i></div>', unsafe_allow_html=True)
            if st.button(page, key=page, type="primary" if is_active else "secondary", use_container_width=True):
                st.session_state.active_page = page
                st.rerun()

        if st.button("Log Out"):
            if st.session_state.get("user"):
                try:
                    auth.revoke_refresh_tokens(st.session_state["user"])
                except Exception as e:
                    st.error(f"Error logging out: {e}")
            st.session_state["logged_in"] = False
            st.session_state["user"] = None
            st.rerun()
    
    return st.session_state.active_page