import streamlit as st
from components.shared import render_sidebar, hide_default_sidebar
from pages import Dashboard, Financial_Health_Monitoring, Nexus, Settings
from login import init_firebase, render_login_form

# --- Page Configuration ---
st.set_page_config(page_title="FinQ", page_icon="📈", layout="wide")

# --- Firebase Initialization ---
firebase_config = init_firebase()

# --- Authentication ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        render_login_form(firebase_config)
else:
    # --- Hide Default Sidebar ---
    hide_default_sidebar()

    # --- Page Navigation ---
    PAGES = {
        "Dashboard": Dashboard,
        "Financial Health Monitoring": Financial_Health_Monitoring,
        "Nexus": Nexus,
        "Settings": Settings,
    }

    # --- Render Sidebar and Page ---
    selected_page = render_sidebar()

    if selected_page in PAGES:
        PAGES[selected_page].render()
    else:
        st.error("Page not found!")