import streamlit as st

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
            st.session_state["logged_in"] = False
            st.session_state["user"] = None
            st.rerun()
    
    return page