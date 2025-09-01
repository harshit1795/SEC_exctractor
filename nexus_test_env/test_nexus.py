import streamlit as st
from components.nexus_config import initialize_firebase
from components.nexus_controller import NexusController
from components.nexus_views import render_profile_tab, render_people_tab, render_posts_tab, render_messages_tab

from components.nexus_agent import NexusAgent

def main():
    st.title("Nexus Test Environment")

    if not initialize_firebase():
        st.error("Failed to initialize Nexus. Please check your Firebase configuration.")
        return

    # Mock user session
    if 'user' not in st.session_state:
        st.session_state.user = {"uid": "test_user_01", "display_name": "Test User"}

    user_id = st.session_state.user['uid']
    st.write(f"Logged in as: **{st.session_state.user['display_name']}** (`{user_id}`)")
    
    agent = NexusAgent()
    controller = agent.get_controller()

    tabs = ["Profile", "Feed", "People", "Messages"]
    selected_tab = st.sidebar.radio("Navigate Nexus", tabs)

    if selected_tab == "Profile":
        render_profile_tab(controller, user_id)
    elif selected_tab == "Feed":
        render_posts_tab(controller, user_id)
    elif selected_tab == "People":
        render_people_tab(controller, user_id)
    elif selected_tab == "Messages":
        render_messages_tab(controller, user_id)

if __name__ == "__main__":
    main()
