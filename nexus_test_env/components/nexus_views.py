import streamlit as st
from components.nexus_controller import NexusController

def render_profile_tab(controller: NexusController, user_id: str):
    st.subheader("My Profile")
    profile = controller.get_or_create_user_profile(user_id)

    if profile:
        st.text_input("Display Name", value=profile.display_name, key="profile_display_name")
        st.text_area("Bio", value=profile.bio, key="profile_bio")
        st.text_input("Location", value=profile.location, key="profile_location")
        st.text_input("Website", value=profile.website, key="profile_website")

        if st.button("Save Profile"):
            profile.display_name = st.session_state.profile_display_name
            profile.bio = st.session_state.profile_bio
            profile.location = st.session_state.profile_location
            profile.website = st.session_state.profile_website
            if controller.update_user_profile(profile):
                st.success("Profile updated successfully!")
            else:
                st.error("Failed to update profile.")

def render_people_tab(controller: NexusController, current_user_id: str):
    st.subheader("People")
    users = controller.get_user_list()
    connections = controller.db.get_user_connections(current_user_id) or controller.db.UserConnections(uid=current_user_id)

    for user in users:
        if user.uid == current_user_id:
            continue
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(user.display_name)
            st.caption(user.bio)
        with col2:
            if user.uid in connections.friends:
                st.button("Remove Friend", key=f"remove_{user.uid}", on_click=controller.remove_friend, args=(current_user_id, user.uid))
            elif user.uid in connections.requests:
                st.write("Request Sent")
            else:
                st.button("Add Friend", key=f"add_{user.uid}", on_click=controller.send_friend_request, args=(current_user_id, user.uid))

def render_posts_tab(controller: NexusController, current_user_id: str):
    st.subheader("Posts")
    connections = controller.db.get_user_connections(current_user_id) or controller.db.UserConnections(uid=current_user_id)
    friend_ids = connections.friends + [current_user_id]
    
    # This is a simplified feed. A real implementation would use pagination.
    posts = []
    for friend_id in friend_ids:
        posts.extend(controller.db.get_user_posts(friend_id, limit=10))
    
    posts.sort(key=lambda x: x.created_at, reverse=True)

    for post in posts:
        with st.container():
            st.write(f"**{controller.get_or_create_user_profile(post.author_id).display_name}** wrote:")
            st.write(post.content)
            st.button(f"❤️ {len(post.likes)} Likes", key=f"like_{post.id}", on_click=controller.like_post, args=(current_user_id, post.id))

def render_messages_tab(controller: NexusController, current_user_id: str):
    st.subheader("Messages")
    connections = controller.db.get_user_connections(current_user_id) or controller.db.UserConnections(uid=current_user_id)
    friends = [controller.get_or_create_user_profile(uid) for uid in connections.friends]
    
    if friends:
        friend_options = {f.display_name: f.uid for f in friends}
        selected_friend_name = st.selectbox("Select a friend to message", options=list(friend_options.keys()))
        
        if selected_friend_name:
            selected_friend_id = friend_options[selected_friend_name]
            conversation = controller.db.get_conversation(current_user_id, selected_friend_id)

            for msg in conversation:
                if msg.from_user == current_user_id:
                    st.write(f"**You:** {msg.text}")
                else:
                    st.write(f"**{selected_friend_name}:** {msg.text}")

            text = st.text_input("Your message:", key=f"msg_to_{selected_friend_id}")
            if st.button("Send", key=f"send_to_{selected_friend_id}"):
                if controller.send_message(current_user_id, selected_friend_id, text):
                    st.success("Message sent!")
                else:
                    st.error("Failed to send message.")
    else:
        st.info("You have no friends to message yet.")
