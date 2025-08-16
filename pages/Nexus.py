import streamlit as st
import json
import os

def render():
    st.markdown("<h2 style='text-align: center;'> Nexus – Community</h2>", unsafe_allow_html=True)

    NEXUS_PATH = "nexus_store.json"

    def _load_nexus() -> dict:
        """Load Nexus community store from disk, validating user profiles and messages."""
        if os.path.exists(NEXUS_PATH):
            try:
                with open(NEXUS_PATH, "r") as f:
                    data = json.load(f)
                    # Validate each user's profile to ensure it's a dictionary
                    for user_key, profile in data.items():
                        if user_key != "_messages" and not isinstance(profile, dict):
                            data[user_key] = {
                                "friends": [],
                                "followers": [],
                                "following": [],
                                "requests": [],
                                "posts": []
                            }
                    # Validate messages
                    if "_messages" in data and isinstance(data["_messages"], list):
                        data["_messages"] = [m for m in data["_messages"] if isinstance(m, dict) and "from" in m and "to" in m and "text" in m]
                    else:
                        data["_messages"] = []
                    return data
            except Exception:
                return {}
        return {}


    def _save_nexus(data: dict):
        """Persist Nexus store to disk."""
        try:
            with open(NEXUS_PATH, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    nx = st.session_state.get("nexus", {})
    user = st.session_state.get("user")
    if user not in nx:
        st.error("Profile not found.")
        st.stop()

    prof = nx[user]

    # If viewing another user's profile
    if st.session_state.get("profile_user") and st.session_state["profile_user"] != user:
        view_user = st.session_state["profile_user"]
        if view_user not in nx:
            st.error("User not found.")
        else:
            vp = nx[view_user]
            st.markdown(f"###  {view_user}'s Page")
            st.markdown(f"**Followers:** {len(vp['followers'])} • **Following:** {len(vp['following'])} • **Friends:** {len(vp['friends'])}")
            if st.button(" Back", key="back_btn"):
                st.session_state.pop("profile_user")
                st.experimental_rerun()

            st.markdown("---")
            st.markdown("#### Threads")
            for post in reversed(vp["posts"]):
                st.markdown(post["content"])
                st.markdown("**Comments:**")
                for c in post["comments"]:
                    st.markdown(f"- *{c['user']}*: {c['text']}")
                st.markdown("---")
            st.stop()

    tab_people, tab_messages, tab_my_page = st.tabs(["People", "Messages", "My Page"])

    # ---------------- People Tab ---------------- #
    with tab_people:
        st.subheader("Community Members")
        search_term = st.text_input("Search users", "", key="user_search")
        others_all = [u for u in nx.keys() if u != user and u != "_messages"]
        if search_term:
            term = search_term.lower()
            others = [u for u in others_all if term in u.lower()]
        else:
            others = others_all

        if not others:
            st.info("No other users yet.")
        for ou in others:
            op = nx[ou]
            cols = st.columns([2,1,1,1])
            cols[0].markdown(f"**{ou}**")
            if ou in prof["friends"]:
                cols[1].markdown("✅ Friend")
            elif ou in prof["requests"]:
                if cols[1].button("Accept", key=f"acc_{ou}"):
                    prof["friends"].append(ou)
                    prof["requests"].remove(ou)
                    nx[ou]["friends"].append(user)
                    _save_nexus(nx)
                    st.experimental_rerun()
            else:
                if cols[1].button("Add Friend", key=f"req_{ou}"):
                    if user not in nx[ou]["requests"]:
                        nx[ou]["requests"].append(user)
                        _save_nexus(nx)
                        st.success("Request sent!")

            # follow / unfollow
            if user in nx[ou]["followers"]:
                if cols[2].button("Unfollow", key=f"unf_{ou}"):
                    nx[ou]["followers"].remove(user)
                    prof["following"].remove(ou)
                    _save_nexus(nx)
                    st.experimental_rerun()
            else:
                if cols[2].button("Follow", key=f"fol_{ou}"):
                    nx[ou]["followers"].append(user)
                    prof["following"].append(ou)
                    _save_nexus(nx)
                    st.experimental_rerun()

            # View page
            if cols[3].button("View Page", key=f"view_{ou}"):
                st.session_state["profile_user"] = ou
                st.experimental_rerun()

    # ---------------- Messages Tab ---------------- #
    with tab_messages:
        st.subheader("Direct Messages")
        friends = prof["friends"]
        if not friends:
            st.info("Add friends to start messaging.")
        else:
            chat_target = st.selectbox("Chat with", friends, key="msg_target")
            # load messages store
            msg_store = nx.get("_messages", [])
            history = [m for m in msg_store if (m["from"]==user and m["to"]==chat_target) or (m["from"]==chat_target and m["to"]==user)]
            for m in history[-20:]:
                align = "▶" if m["from"]==user else "◀"
                st.markdown(f"{align} **{m['from']}**: {m['text']}")
            new_msg = st.text_input("Type a message", key="msg_input")
            if st.button("Send", key="msg_send") and new_msg.strip():
                msg_store.append({"from":user,"to":chat_target,"text":new_msg})
                nx["_messages"] = msg_store
                _save_nexus(nx)
                st.experimental_rerun()

    # ---------------- My Page Tab ---------------- #
    with tab_my_page:
        st.subheader("My Page / Threads")
        post_text = st.text_area("Write a post (max 500 words)", max_chars=3000, key="post_text")
        if st.button("Publish", key="post_pub") and post_text.strip():
            words = len(post_text.split())
            if words>500:
                st.error("Post exceeds 500 words.")
            else:
                prof["posts"].append({"content": post_text, "comments": []})
                _save_nexus(nx)
                st.success("Posted!")

        st.markdown("---")
        st.markdown("### My Posts")
        for idx,p in enumerate(reversed(prof["posts"])):
            st.markdown(p["content"])
            st.markdown("**Comments:**")
            for c in p["comments"]:
                st.markdown(f"- *{c['user']}*: {c['text']}")
            comment_key = f"com_{idx}"
            new_c = st.text_input("Add comment", key=comment_key)
            if st.button("Comment", key=comment_key+"btn") and new_c.strip():
                p["comments"].append({"user":user, "text":new_c})
                _save_nexus(nx)
                st.experimental_rerun()
