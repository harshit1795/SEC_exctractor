"""
Profile Tab for Nexus Module

This tab displays and allows editing of user profiles.
"""

import streamlit as st
from components.nexus_firebase import get_user_profile, update_user_profile, get_user_posts, update_post, delete_post

def render():
    st.header("My Profile")

    if 'user_info' not in st.session_state or not st.session_state.user_info:
        st.warning("Please log in to see your profile.")
        return

    user_id = st.session_state.user_info['uid']
    profile = get_user_profile(user_id)

    if profile is None:
        st.info("You don't have a profile yet. Let's create one!")
        with st.form("create_profile_form"):
            st.write("Create your profile:")
            display_name = st.text_input("Display Name")
            bio = st.text_area("Bio")
            profile_picture_url = st.text_input("Profile Picture URL")

            submitted = st.form_submit_button("Create Profile")

            if submitted:
                new_data = {
                    "displayName": display_name,
                    "bio": bio,
                    "profilePictureUrl": profile_picture_url,
                    "friends": []
                }
                if update_user_profile(user_id, new_data):
                    st.success("Profile created successfully!")
                    st.rerun()
                else:
                    st.error("Failed to create profile.")
    else:
        # Display Profile
        col1, col2 = st.columns([1, 3])
        with col1:
            if profile.get("profilePictureUrl"):
                st.image(profile["profilePictureUrl"], width=150)
            else:
                st.image("https://via.placeholder.com/150", width=150)

        with col2:
            st.subheader(profile.get("displayName", "New User"))
            st.write(profile.get("bio", "No bio yet."))

        st.divider()

        # Edit Profile Form
        with st.expander("Edit Profile"):
            with st.form("edit_profile_form"):
                st.write("Update your profile information:")
                display_name = st.text_input("Display Name", value=profile.get("displayName", ""))
                bio = st.text_area("Bio", value=profile.get("bio", ""))
                profile_picture_url = st.text_input("Profile Picture URL", value=profile.get("profilePictureUrl", ""))

                submitted = st.form_submit_button("Save Changes")

                if submitted:
                    new_data = {
                        "displayName": display_name,
                        "bio": bio,
                        "profilePictureUrl": profile_picture_url
                    }
                    if update_user_profile(user_id, new_data):
                        st.success("Profile updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update profile.")
        
        st.divider()

        # Display User's Posts
        st.subheader("My Posts")
        user_posts = get_user_posts(user_id)

        if not user_posts:
            st.info("You have not created any posts yet.")
        else:
            for post in user_posts:
                st.markdown(f"""<div style='border: 1px solid #ccc; border-radius: 5px; padding: 10px; margin-bottom: 10px;'>
                    {post['content']}
                </div>""", unsafe_allow_html=True)

                # Timestamp and Edit/Delete buttons
                col1, col2, col3 = st.columns([8, 1, 1])
                with col1:
                    if 'lastEdited' in post:
                        st.caption(f"Last edited on: {post['lastEdited'].strftime('%Y-%m-%d %H:%M')}")
                    else:
                        st.caption(f"Posted on: {post['timestamp'].strftime('%Y-%m-%d %H:%M')}")
                with col2:
                    if st.button("Edit", key=f"edit_{post['id']}"):
                        st.session_state.editing_post_id = post['id']
                with col3:
                    if st.button("Delete", key=f"delete_{post['id']}"):
                        st.session_state.deleting_post_id = post['id']
                
                # Edit form
                if st.session_state.get('editing_post_id') == post['id']:
                    with st.form(f"edit_form_{post['id']}"):
                        new_content = st.text_area("Edit your post", value=post['content'])
                        if st.form_submit_button("Save Changes"):
                            if update_post(post['id'], new_content):
                                st.success("Post updated successfully!")
                                del st.session_state.editing_post_id
                                st.rerun()
                            else:
                                st.error("Failed to update post.")

                # Delete confirmation
                if st.session_state.get('deleting_post_id') == post['id']:
                    st.warning(f"Are you sure you want to delete this post? This action cannot be undone.")
                    if st.button("Yes, delete it", key=f"confirm_delete_{post['id']}"):
                        if delete_post(post['id']):
                            st.success("Post deleted successfully!")
                            del st.session_state.deleting_post_id
                            st.rerun()
                        else:
                            st.error("Failed to delete post.")

                st.divider()
