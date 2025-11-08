"""
Friends Tab for Nexus Module

This tab displays the user's friend list and pending friend requests.
"""

import streamlit as st
from components.nexus_firebase import (
    get_friend_requests,
    accept_friend_request,
    reject_friend_request,
    get_friends,
    get_user_profile
)

def render():
    st.header("Friends and Friend Requests")

    if 'user_info' not in st.session_state or not st.session_state.user_info:
        st.warning("Please log in to see your friends.")
        return

    current_user_id = st.session_state.user_info['uid']

    # Display Friend Requests
    st.subheader("Friend Requests")
    friend_requests = get_friend_requests(current_user_id)

    if not friend_requests:
        st.info("You have no pending friend requests.")
    else:
        for request in friend_requests:
            from_user_id = request['fromUserId']
            from_user_profile = get_user_profile(from_user_id)
            if from_user_profile:
                col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
                with col1:
                    if from_user_profile.get("profilePictureUrl"):
                        st.image(from_user_profile["profilePictureUrl"], width=50)
                    else:
                        st.image("https://via.placeholder.com/150", width=50)
                with col2:
                    st.write(from_user_profile.get("displayName", "Unknown User"))
                with col3:
                    if st.button("Accept", key=f"accept_{request['id']}"):
                        if accept_friend_request(request['id'], from_user_id, current_user_id):
                            st.success("Friend request accepted!")
                            st.rerun()
                        else:
                            st.error("Failed to accept friend request.")
                with col4:
                    if st.button("Reject", key=f"reject_{request['id']}"):
                        if reject_friend_request(request['id']):
                            st.success("Friend request rejected.")
                            st.rerun()
                        else:
                            st.error("Failed to reject friend request.")

    st.divider()

    # Display Friends List
    st.subheader("My Friends")
    friends = get_friends(current_user_id)

    if not friends:
        st.info("You have no friends yet. Go to the User Directory to add some!")
    else:
        for friend in friends:
            col1, col2 = st.columns([1, 3])
            with col1:
                if friend.get("profilePictureUrl"):
                    st.image(friend["profilePictureUrl"], width=75)
                else:
                    st.image("https://via.placeholder.com/150", width=75)
            with col2:
                st.subheader(friend.get("displayName", "Unknown User"))
                st.write(friend.get("bio", "No bio yet."))
            st.divider()
