
import streamlit as st
from fb_streamlit_auth import fb_streamlit_auth
import json
import os
import firebase_admin
from firebase_admin import credentials
from components.shared import hide_default_sidebar
import time

def init_firebase():
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
        
    return firebase_config

def render_login_form(firebase_config):
    hide_default_sidebar()
    st.image("FInQLogo.png", width=200)
    st.title("Welcome to FinQ")

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
            # Simulate loading time for demonstration. Remove in production if not needed.
            time.sleep(2)
            st.rerun()

