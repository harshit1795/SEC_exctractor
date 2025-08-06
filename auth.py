import os
import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
import streamlit.components.v1 as components

# --- Firebase Initialization ---

# Check if Firebase app is already initialized
if not firebase_admin._apps:
    try:
        # Try to use credentials from Streamlit secrets first
        cred = credentials.Certificate(st.secrets["firebase_credentials"])
    except (KeyError, FileNotFoundError):
        # Fallback to a local file for development
        if os.path.exists("firebase-credentials.json"):
            cred = credentials.Certificate("firebase-credentials.json")
        else:
            st.error("Firebase credentials not found. Please add them to your Streamlit secrets or create a 'firebase-credentials.json' file.")
            st.stop()
    
    firebase_admin.initialize_app(cred)

db = firestore.client()

def get_firebase_config():
    """Loads Firebase config from secrets or a local file."""
    try:
        return st.secrets["firebase_config"]
    except (KeyError, FileNotFoundError):
        if os.path.exists("firebase-config.json"):
            with open("firebase-config.json") as f:
                return json.load(f)
        else:
            st.error("Firebase config not found. Please add it to your Streamlit secrets or create a 'firebase-config.json' file.")
            st.stop()

# --- User Authentication ---

def get_or_create_user(email):
    """Get a user by email, or create a new one if they don't exist."""
    try:
        user = auth.get_user_by_email(email)
        return user
    except auth.UserNotFoundError:
        user = auth.create_user(email=email)
        # Create an empty preferences document for the new user
        db.collection("user_prefs").document(user.uid).set({})
        return user
    except Exception as e:
        st.error(f"Error getting or creating user: {e}")
        return None

def login_user(email):
    """Logs in a user by setting the session state."""
    user = get_or_create_user(email)
    if user:
        st.session_state["user"] = user.uid
        st.session_state["logged_in"] = True
    return user

def show_login_ui():
    """Displays the Firebase login UI and handles the authentication flow."""
    st.markdown("<style>[data-testid='stSidebar'] { display: none; }</style>", unsafe_allow_html=True)

    st.image("FInQLogo.png", width=200)
    st.title("Welcome to FinQ! 👋")

    firebase_config = get_firebase_config()

    html = f"""
        <script src="https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js"></script>
        <script src="https://www.gstatic.com/firebasejs/9.6.1/firebase-auth.js"></script>
        <script src="https://www.gstatic.com/firebasejs/ui/6.0.1/firebase-ui-auth.js"></script>
        <link type="text/css" rel="stylesheet" href="https://www.gstatic.com/firebasejs/ui/6.0.1/firebase-ui-auth.css" />

        <div id="firebaseui-auth-container"></div>

        <script>
            const firebaseConfig = {json.dumps(firebase_config)};
            // Check if Firebase app is already initialized
            if (!firebase.apps.length) {{
                firebase.initializeApp(firebaseConfig);
            }}

            var uiConfig = {{
                callbacks: {{
                    signInSuccessWithAuthResult: function(authResult, redirectUrl) {{
                        if (authResult.user) {{
                            const email = authResult.user.email;
                            const url = new URL(window.location.href);
                            url.searchParams.set('email', email);
                            window.location.href = url.href;
                        }}
                        return false;
                    }}
                }},
                signInOptions: [
                    firebase.auth.GoogleAuthProvider.PROVIDER_ID
                ],
                signInFlow: 'popup'
            }};

            var ui = firebaseui.auth.AuthUI.getInstance() || new firebaseui.auth.AuthUI(firebase.auth());
            ui.start('#firebaseui-auth-container', uiConfig);
        </script>
    """

    components.html(html, height=500)

    query_params = st.experimental_get_query_params()
    if "email" in query_params:
        email = query_params["email"][0]
        login_user(email)
        st.experimental_set_query_params() # Clear the query params
        st.experimental_rerun()

# --- User Preferences (Firestore) ---

def _load_user_prefs() -> dict:
    """Load user preferences from Firestore."""
    if "user" not in st.session_state:
        return {{}}
        
    user_uid = st.session_state["user"]
    doc_ref = db.collection("user_prefs").document(user_uid)
    doc = doc_ref.get()
    
    if doc.exists:
        return doc.to_dict()
    return {{}}

def _save_user_prefs(prefs: dict):
    """Save user preferences to Firestore."""
    if "user" not in st.session_state:
        return
        
    user_uid = st.session_state["user"]
    doc_ref = db.collection("user_prefs").document(user_uid)
    doc_ref.set(prefs)

# --- API Key Management ---

def load_api_keys():
    """Load API keys from user preferences and configure services."""
    if "user" not in st.session_state:
        return False

    user_prefs = _load_user_prefs()
    gemini_key = user_prefs.get("GEMINI_API_KEY")
    fred_key = user_prefs.get("FRED_API_KEY")

    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key
    if fred_key:
        os.environ["FRED_API_KEY"] = fred_key

    if os.environ.get("GEMINI_API_KEY"):
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.environ["GEMINI_API_KEY"])
            return True
        except Exception as e:
            st.error(f"Failed to configure Gemini: {e}")
            return False
    else:
        st.warning("GEMINI_API_KEY is not set. Please add it in the Settings page.")
        return False

# --- Nexus Community Feed (Firestore) ---

def load_nexus_feed() -> list:
    """Load the Nexus community feed from Firestore."""
    doc_ref = db.collection("nexus_data").document("feed")
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict().get("items", [])
    return []

def save_nexus_feed(feed_data: list):
    """Save the Nexus community feed to Firestore."""
    doc_ref = db.collection("nexus_data").document("feed")
    doc_ref.set({"items": feed_data})
