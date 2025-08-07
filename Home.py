import streamlit as st
import firebase_admin
from firebase_admin import credentials
import json
import streamlit_firebase_auth as sfa
import os

# --- Page Configuration ---
st.set_page_config(page_title="FinQ", page_icon="📈", layout="centered")

# --- Firebase Initialization ---
if not firebase_admin._apps:
    try:
        firebase_creds_dict = st.secrets["firebase_credentials"]
    except (KeyError, FileNotFoundError):
        if os.path.exists("firebase-credentials.json"):
            with open("firebase-credentials.json") as f:
                firebase_creds_dict = json.load(f)
        else:
            st.error("Firebase credentials not found.")
            st.stop()
            
    cred = credentials.Certificate(firebase_creds_dict)
    firebase_admin.initialize_app(cred)

try:
    with open("firebase-config.json") as f:
        firebase_config = json.load(f)
except (KeyError, FileNotFoundError):
    firebase_config = st.secrets["firebase_config"]

# --- Session State Initialization ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None

def display_splash_screen():
    """Displays the splash screen with a Google Sign-In button."""
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                display: none
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    st.image("FInQLogo.png", width=200)
    st.title("Welcome to FinQ")

    choice = st.selectbox("Login/Signup", ["Login", "Signup"])

    if choice == "Login":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = sfa.login(email, password, firebase_config)
            if user:
                st.session_state["user"] = user['uid']
                st.session_state["logged_in"] = True
                st.rerun()
    else:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Signup"):
            user = sfa.signup(email, password, firebase_config)
            if user:
                st.success("Signup successful! Please login.")

def display_main_app():
    # ... (rest of the function remains the same) ...
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
        options=["Dashboard", "Financial Health Monitoring", "Nexus", "Settings"],
        key="navigation_main"
    )

    if st.sidebar.button("Log Out"):
        st.session_state["logged_in"] = False
        st.session_state["user"] = None
        st.rerun()

    if page == "Dashboard":
        st.switch_page("pages/0_Dashboard.py")
    elif page == "Financial Health Monitoring":
        st.switch_page("pages/1_Financial_Health_Monitoring.py")
    elif page == "Nexus":
        st.switch_page("pages/2_Nexus.py")
    elif page == "Settings":
        st.switch_page("pages/4_Settings.py")


# --- Main Application Logic ---
if st.session_state.get("logged_in"):
    display_main_app()
else:
    display_splash_screen()
