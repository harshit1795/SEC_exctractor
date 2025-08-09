import streamlit as st

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
            st.switch_page("login.py")
    
    return page