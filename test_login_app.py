import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
from fb_streamlit_auth import fb_streamlit_auth
import os
import json

# --- Firebase Initialization ---
def init_firebase():
    try:
        # This part is for Streamlit Cloud deployment, using secrets
        firebase_creds_dict = {
            "type": st.secrets["FIREBASE_CRED_TYPE"],
            "project_id": st.secrets["FIREBASE_CRED_PROJECT_ID"],
            "private_key_id": st.secrets["FIREBASE_CRED_PRIVATE_KEY_ID"],
            "private_key": st.secrets["FIREBASE_CRED_PRIVATE_KEY"].replace('\\n', '\n'),
            "client_email": st.secrets["FIREBASE_CRED_CLIENT_EMAIL"],
            "client_id": st.secrets["FIREBASE_CRED_CLIENT_ID"],
            "auth_uri": st.secrets["FIREBASE_CRED_AUTH_URI"],
            "token_uri": st.secrets["FIREBASE_CRED_TOKEN_URI"],
            "auth_provider_x509_cert_url": st.secrets["FIREBASE_CRED_AUTH_PROVIDER_X509_CERT_URL"],
            "client_x509_cert_url": st.secrets["FIREBASE_CRED_CLIENT_X509_CERT_URL"],
            "universe_domain": st.secrets["FIREBASE_CRED_UNIVERSE_DOMAIN"]
        }
        firebase_config = {
            "apiKey": st.secrets["FIREBASE_API_KEY"],
            "authDomain": st.secrets["FIREBASE_AUTH_DOMAIN"],
            "projectId": st.secrets["FIREBASE_PROJECT_ID"],
            "storageBucket": st.secrets["FIREBASE_STORAGE_BUCKET"],
            "messagingSenderId": st.secrets["FIREBASE_MESSAGING_SENDER_ID"],
            "appId": st.secrets["FIREBASE_APP_ID"],
            "measurementId": st.secrets.get("FIREBASE_MEASUREMENT_ID", "")
        }
    except (KeyError, FileNotFoundError):
        # Fallback for local development
        if os.path.exists("firebase-credentials.json") and os.path.exists("firebase-config.json"):
            with open("firebase-credentials.json") as f:
                firebase_creds_dict = json.load(f)
            with open("firebase-config.json") as f:
                firebase_config = json.load(f)
        else:
            st.error("Firebase configuration not found. Please set up secrets or local files.")
            st.stop()

    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_creds_dict)
        firebase_admin.initialize_app(cred)
        
    return firebase_config

def render_logout_js(firebase_config):
    # This function injects JavaScript to perform a client-side logout
    # It uses the Firebase JS SDK to sign out the user and then reloads the page
    config_json = json.dumps(firebase_config)
    js_template = f'''
    <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
    <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-auth.js"></script>
    <script>
        const firebaseConfig = {config_json};
        if (!firebase.apps.length) {{
            firebase.initializeApp(firebaseConfig);
        }}
        firebase.auth().signOut().then(() => {{
            // Force a reload of the page to clear all state and show the login form
            window.parent.location.reload();
        }}).catch((error) => {{
            console.error("Sign out error", error);
        }});
    </script>
    '''
    st.components.v1.html(js_template, height=0)

# --- Main App Logic ---
st.set_page_config(page_title="Login Test App", page_icon="🧪")
st.title("🧪 Firebase Login Test")

firebase_config = init_firebase()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- Render Welcome Screen or Login Form ---
if st.session_state['logged_in']:
    # --- Welcome Screen ---
    st.success(f"Welcome, {st.session_state.get('user_name', 'User')}!")
    st.write("You are logged in.")
    if st.button("Log Out"):
        # Step 1: Revoke the server-side token for security
        if st.session_state.get("user"):
            try:
                auth.revoke_refresh_tokens(st.session_state["user"])
            except Exception as e:
                st.warning(f"Could not revoke refresh tokens: {{e}}")
        
        # Step 2: Trigger the client-side logout using JavaScript
        render_logout_js(firebase_config)

        # Step 3: Clear the server-side session state
        st.session_state['logged_in'] = False
        st.session_state.pop('user', None)
        st.session_state.pop('user_name', None)
        # No rerun here, the JS reload handles it
else:
    # --- Login Form ---
    st.write("Please log in to continue.")
    try:
        user = fb_streamlit_auth(
            apiKey=firebase_config["apiKey"],
            authDomain=firebase_config["authDomain"],
            databaseURL=firebase_config.get("databaseURL", ""),
            projectId=firebase_config["projectId"],
            storageBucket=firebase_config["storageBucket"],
            messagingSenderId=firebase_config["messagingSenderId"],
            appId=firebase_config["appId"],
            measurementId=firebase_config.get("measurementId", ""),
        )

        if user:
            st.session_state["user"] = user['uid']
            st.session_state["logged_in"] = True
            st.session_state["user_name"] = user.get('displayName', 'N/A')
            st.rerun()

    except Exception as e:
        st.error(f"An error occurred during authentication: {{e}}")
