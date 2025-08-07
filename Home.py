import streamlit as st

# --- Page Configuration ---
st.set_page_config(page_title="FinQ", page_icon="📈", layout="centered")

# --- Authentication Check ---
if not st.session_state.get("logged_in"):
    st.switch_page("login.py")

def display_main_app():
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] { display: block }
            [data-testid="stHeader"] { display: block }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.image("FInQLogo.png", width=100)
    st.sidebar.title("FinQ Modules")

    page = st.sidebar.radio(
        "Navigation",
        options=["Dashboard", "Financial Health Monitoring", "Nexus", "About", "Contact", "Settings"],
        key="navigation_main"
    )

    if st.sidebar.button("Log Out"):
        st.session_state["logged_in"] = False
        st.session_state["user"] = None
        st.switch_page("login.py")

    if page == "Dashboard":
        st.switch_page("pages/0_Dashboard.py")
    elif page == "Financial Health Monitoring":
        st.switch_page("pages/1_Financial_Health_Monitoring.py")
    elif page == "Nexus":
        st.switch_page("pages/2_Nexus.py")
    elif page == "About":
        st.switch_page("pages/3_About.py")
    elif page == "Contact":
        st.switch_page("pages/5_Contact.py")
    elif page == "Settings":
        st.switch_page("pages/4_Settings.py")

# --- Main Application Logic ---
display_main_app()
