
import streamlit as st
from auth import load_nexus_feed, save_nexus_feed

# --- Page Setup ---
st.set_page_config(page_title="Nexus - FinQ", page_icon="🌐")

# --- Authentication Check ---
if not st.session_state.get("logged_in"):
    st.warning("Please log in to access the Nexus community.")
    st.switch_page("Home.py")
    st.stop()

# --- Nexus Feed ---
st.markdown("<h2 style='text-align: center;'>🌐 Nexus Community Feed</h2>", unsafe_allow_html=True)

# Load the feed from Firestore
nexus_feed = load_nexus_feed()

# Display the feed
for item in reversed(nexus_feed):
    st.markdown(f"**{item['author']}** says:")
    st.info(item['content'])

# Add a new post
new_post = st.text_area("Share your insights with the community:")
if st.button("Post to Nexus"):
    if new_post:
        nexus_feed.append({"author": st.session_state["user"], "content": new_post})
        save_nexus_feed(nexus_feed)
        st.success("Your post has been added to the Nexus feed!")
        st.rerun()
    else:
        st.warning("Please enter a message to post.")

# --- Back to Home ---
if st.button("Back to Main Menu"):
    st.switch_page("Home.py")
