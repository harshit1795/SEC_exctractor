"""
User Directory Tab for Nexus Module

This tab displays a list of all users and allows sending friend requests.
"""

import streamlit as st
from components.nexus_firebase import get_all_users, send_friend_request, get_user_profile

def render():
    st.header("User Directory")

    if 'user_info' not in st.session_state or not st.session_state.user_info:
        st.warning("Please log in to see the user directory.")
        return

    current_user_id = st.session_state.user_info['uid']
    all_users = get_all_users()
    current_user_profile = get_user_profile(current_user_id)

    if not all_users:
        st.info("No other users found.")
        return

    for user in all_users:
        if user['uid'] == current_user_id or not user.get("displayName"):
            continue

        col1, col2, col3 = st.columns([1, 3, 1])

        with col1:
            if user.get("profilePictureUrl"):
                st.image(user["profilePictureUrl"], width=75)
            else:
                st.image("https://via.placeholder.com/150", width=75)

        with col2:
            st.subheader(user.get("displayName", "New User"))
            st.write(user.get("bio", "No bio yet."))

        with col3:
            # Friend request button logic
            is_friend = user['uid'] in current_user_profile.get('friends', [])
            if not is_friend:
                if st.button(f"Send Friend Request", key=f"request_{user['uid']}"):
                    if send_friend_request(current_user_id, user['uid']):
                        st.success(f"Friend request sent to {user.get('displayName')}")
                        st.rerun()
                    else:
                        st.error("Failed to send friend request.")
            else:
                st.success("Already friends")

        st.divider()
