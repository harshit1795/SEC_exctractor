import streamlit as st
from fb_streamlit_auth import fb_streamlit_auth
import json
import os
import firebase_admin
from firebase_admin import credentials
from components.shared import hide_default_sidebar
import time

def init_firebase():
    try:
        # Try to get Firebase credentials from Streamlit secrets first (for cloud deployment)
        firebase_creds_dict = {
            "type": st.secrets["FIREBASE_CRED_TYPE"],
            "project_id": st.secrets["FIREBASE_CRED_PROJECT_ID"],
            "private_key_id": st.secrets["FIREBASE_CRED_PRIVATE_KEY_ID"],
            "private_key": st.secrets["FIREBASE_CRED_PRIVATE_KEY"].replace('\n', '\n'),
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
    except KeyError:
        # If secrets are not found, fallback to local files (for local development)
        if os.path.exists("firebase-credentials.json") and os.path.exists("firebase-config.json"):
            with open("firebase-credentials.json") as f:
                firebase_creds_dict = json.load(f)
            with open("firebase-config.json") as f:
                firebase_config = json.load(f)
        else:
            st.error("Firebase configuration not found. Please set up your secrets or local config files.")
            st.stop()

    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_creds_dict)
        firebase_admin.initialize_app(cred)
        
    return firebase_config

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
    
    # Add some styling for better appearance
    st.markdown("""
    <style>
    .login-container {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 10px;
        margin: 2rem 0;
    }
    .login-button {
        background-color: #ff4b4b;
        color: white;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
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
                    st.session_state["user"] = user['uid']
                    st.session_state["logged_in"] = True
                    st.session_state["user_email"] = user.get('email', '')
                    st.session_state["user_name"] = user.get('displayName', '')
                    
                    # Show success message
                    st.success(f"Welcome back, {user.get('displayName', 'User')}!")
                    
                    # Simulate loading time for demonstration
                    time.sleep(1.5)
                    st.rerun()
                    
        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            st.info("Please check your Firebase configuration and try again.")
            
            # Fallback login option
            st.markdown("---")
            st.markdown("### Alternative Login")
            if st.button("Continue as Guest (Demo Mode)"):
                st.session_state["user"] = "demo_user"
                st.session_state["logged_in"] = True
                st.session_state["user_email"] = "demo@finq.com"
                st.session_state["user_name"] = "Demo User"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Add helpful information
    st.markdown("---")
    st.markdown("""
    **Need help?** 
    - Ensure you have a Google account
    - Check that pop-ups are enabled in your browser
    - Contact support if issues persist
    """)