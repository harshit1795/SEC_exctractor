import streamlit as st
import json
import os

USER_PREFS_FILE = "user_prefs.json"

def load_user_prefs():
    if os.path.exists(USER_PREFS_FILE):
        with open(USER_PREFS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user_prefs(prefs):
    with open(USER_PREFS_FILE, "w") as f:
        json.dump(prefs, f, indent=4)

def hide_default_sidebar():
    st.markdown("""
        <style>
            div[data-testid="stSidebarNav"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)