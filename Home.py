
import streamlit as st
import streamlit.components.v1 as components
import os
from auth import verify_id_token, load_api_keys

st.set_page_config(page_title="FinQ", page_icon="📈")

# --- Authentication ---

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.image("FInQLogo.png", width=200)
    st.title("Welcome to FinQ! 👋")

    # Load the FirebaseUI HTML file
    with open("firebase_ui_auth.html", "r") as f:
        firebase_ui_html = f.read()

    # Render the FirebaseUI component
    auth_response = components.html(firebase_ui_html, height=400)

    if auth_response and "id_token" in auth_response:
        id_token = auth_response["id_token"]
        if verify_id_token(id_token):
            st.experimental_rerun() # Rerun the app to show the main content
else:
    # --- Main Application ---
    
    # Load API keys using the new auth module
    load_api_keys()

    st.sidebar.success("You are logged in.")
    
    st.markdown("<style> .css-1d3f8as { display: flex; flex-direction: column; align-items: center; } </style>", unsafe_allow_html=True)
    st.markdown("<style> img { display: block; margin-left: auto; margin-right: auto; } </style>", unsafe_allow_html=True)
    st.image("FInQLogo.png", width=200)
    st.title("Welcome to FinQ! 👋")

    st.markdown(
        """
        **FinQ is your personal financial analysis assistant.**

        This application allows you to explore and analyze financial data for S&P 500 companies.

        ### Key Features:
        *   **Latest Financial Metric Analysis:** Dive deep into the latest financial metrics of your chosen companies.
        *   **Financial Health Monitoring:** Keep a close eye on the financial health of your portfolio.
        *   **Nexus (Community):** Connect with other investors and share your insights.

        **👈 Select 'Financial Analysis' from the sidebar to get started!**
        """
    )

    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.experimental_rerun()
