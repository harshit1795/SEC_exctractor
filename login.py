import streamlit as st
from fb_streamlit_auth import fb_streamlit_auth
import json
import os
import firebase_admin
from firebase_admin import credentials, auth
from components.utils import hide_default_sidebar
import time

def init_firebase():
    # This function initializes Firebase using credentials from Streamlit secrets for cloud deployment,
    # and falls back to a local JSON file for local development.

    try:
        # First, try to load credentials from Streamlit secrets (for cloud deployment)
        creds_json_str = st.secrets["FIREBASE_CREDENTIALS_JSON"]
        firebase_creds_dict = json.loads(creds_json_str)
    except (KeyError, json.JSONDecodeError):
        # If secrets fail, fall back to local file (for local development)
        if os.path.exists("firebase-credentials.json"):
            with open("firebase-credentials.json") as f:
                firebase_creds_dict = json.load(f)
        else:
            st.error("Firebase credentials not found. Please set up your FIREBASE_CREDENTIALS_JSON secret in Streamlit Cloud or ensure firebase-credentials.json exists for local development.")
            st.stop()

    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(firebase_creds_dict)
            firebase_admin.initialize_app(cred, {
                'projectId': firebase_creds_dict['project_id'],
            })
        except Exception as e:
            st.error(f"Failed to initialize Firebase: {e}")
            st.stop()

    # Load the web app config, which is needed for the frontend authentication component
    try:
        firebase_config = {
            "apiKey": st.secrets["FIREBASE_API_KEY"],
            "authDomain": st.secrets["FIREBASE_AUTH_DOMAIN"],
            "projectId": st.secrets["FIREBASE_PROJECT_ID"],
            "storageBucket": st.secrets["FIREBASE_STORAGE_BUCKET"],
            "messagingSenderId": st.secrets["FIREBASE_MESSAGING_SENDER_ID"],
            "appId": st.secrets["FIREBASE_APP_ID"],
            "measurementId": st.secrets.get("FIREBASE_MEASUREMENT_ID", "")
        }
    except KeyError as e:
        st.error(f"Firebase web app configuration key not found in Streamlit secrets: {e}. Please check your .streamlit/secrets.toml file.")
        st.stop()
        
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

def render_login_form(firebase_config):
    hide_default_sidebar()
    
    # Display logo
    try:
        st.image("FInQLogo.png", width=200)
    except:
        st.title("📈 FinQ")
    
    st.title("Welcome to FinQ")
    st.markdown("### Personal Financial Intelligence & Analytics / AI Platform ###")
    st.markdown("### Leverage and Connect with Leading Financial Information enhanced for use through AI ###")
    
    with st.container():
        # Firebase Authentication
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
                with st.spinner("Loading application... Please wait."):
                    st.session_state["user_info"] = user
                    st.session_state["logged_in"] = True
                    
                    # Show success message
                    st.success(f"Welcome back, {user.get('displayName', 'User')}!")
                    
                    # Simulate loading time for demonstration
                    time.sleep(1.5)
                    st.rerun()
                    
        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            st.info("Please check your Firebase configuration and try again.")
            
    # Add helpful information
    st.markdown("---")
    st.markdown("""
    **Need help?** 
    - Ensure you have a Google account
    - Check that pop-ups are enabled in your browser
    - Contact support if issues persist
    """)

def logout(firebase_config):
    st.info(f"Logging you out..")
    if st.session_state.get("user_info"):
        try:
            auth.revoke_refresh_tokens(st.session_state.user_info['uid'])
        except Exception as e:
            st.error(f"Logout Error.. {e}")
    st.session_state['logged_in'] = False
    st.session_state.pop('user_info', None)
    render_logout_js(firebase_config)