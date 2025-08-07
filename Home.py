import streamlit as st
import firebase_admin
from firebase_admin import credentials
from auth import verify_google_token
import json

# --- Page Configuration ---
st.set_page_config(page_title="FinQ", page_icon="📈", layout="centered")

# --- Firebase Initialization ---
if not firebase_admin._apps:
    try:
        firebase_creds = st.secrets["firebase_credentials"]
    except (KeyError, FileNotFoundError):
        if os.path.exists("firebase-credentials.json"):
            with open("firebase-credentials.json") as f:
                firebase_creds = json.load(f)
        else:
            st.error("Firebase credentials not found.")
            st.stop()
            
    cred = credentials.Certificate(firebase_creds)
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

    # Embedded HTML and Javascript for Google Sign-In
    html_string = f"""
    <script src="https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.6.1/firebase-auth.js"></script>
    <script>
        const firebaseConfig = {json.dumps(firebase_config)};
        const app = firebase.initializeApp(firebaseConfig);
        const auth = firebase.auth();

        function signInWithGoogle() {{
            const provider = new firebase.auth.GoogleAuthProvider();
            auth.signInWithPopup(provider)
                .then((result) => {{
                    const idToken = result.credential.idToken;
                    window.parent.postMessage({{
                        'type': 'streamlit:setComponentValue',
                        'value': idToken
                    }}, '*')
                }})
                .catch((error) => {{
                    console.error("Error during sign-in:", error);
                }});
        }}
    </script>
    <button onclick="signInWithGoogle()">Sign in with Google</button>
    """
    
    id_token = st.html(html_string, height=100)
    
    if id_token:
        decoded_token = verify_google_token(id_token)
        if decoded_token:
            st.session_state["user"] = decoded_token['uid']
            st.session_state["logged_in"] = True
            st.rerun()

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
