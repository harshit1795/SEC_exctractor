import streamlit as st
from components.nexus_firebase import create_post, get_friends_posts, get_user_profile, like_post, unlike_post, add_comment

def render():
    st.header("My Feed")

    if 'user_info' not in st.session_state or not st.session_state.user_info:
        st.warning("Please log in to see your feed.")
        return

    current_user_id = st.session_state.user_info['uid']

    # Create Post Form
    with st.form("create_post_form"):
        content = st.text_area("What's on your mind?")
        submitted = st.form_submit_button("Post")

        if submitted:
            if content:
                if create_post(current_user_id, content):
                    st.success("Post created successfully!")
                    st.rerun()
                else:
                    st.error("Failed to create post.")
            else:
                st.warning("Post content cannot be empty.")

    st.divider()

    # Display Feed
    st.subheader("Posts from your friends")
    friends_posts = get_friends_posts(current_user_id)

    if not friends_posts:
        st.info("Your feed is empty. Add some friends to see their posts!")
    else:
        for post in friends_posts:
            author_profile = get_user_profile(post['authorId'])
            if author_profile:
                col1, col2 = st.columns([1, 7])
                with col1:
                    if author_profile.get("profilePictureUrl"):
                        st.image(author_profile["profilePictureUrl"], width=50)
                    else:
                        st.image("https://via.placeholder.com/150", width=50)
                with col2:
                    st.write(f"**{author_profile.get('displayName', 'Unknown User')}**")
                    st.write(post['content'])
                    st.caption(f"Posted on: {post['timestamp'].strftime('%Y-%m-%d %H:%M')}")

                # Like button and count
                likes = post.get('likes', [])
                liked_by_user = current_user_id in likes

                like_button_text = "Unlike" if liked_by_user else "Like"
                if st.button(like_button_text, key=f"like_{post['id']}"):
                    if liked_by_user:
                        unlike_post(post['id'], current_user_id)
                    else:
                        like_post(post['id'], current_user_id)
                    st.rerun()
                
                st.write(f"{len(likes)} likes")

                # Comments section
                st.write("**Comments**")
                comments = post.get('comments', [])
                for comment in comments:
                    commenter_profile = get_user_profile(comment['userId'])
                    if commenter_profile:
                        st.write(f"**{commenter_profile.get('displayName', 'Unknown User')}**: {comment['text']}")

                # Add a comment
                comment_text = st.text_input("Add a comment", key=f"comment_{post['id']}")
                if st.button("Post Comment", key=f"post_comment_{post['id']}"):
                    if comment_text:
                        add_comment(post['id'], current_user_id, comment_text)
                        st.rerun()

            st.divider()
