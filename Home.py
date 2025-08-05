
import streamlit as st
from auth import login_user, load_api_keys
import webbrowser

st.set_page_config(page_title="FinQ", page_icon="📈")

# --- Authentication ---

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.image("FInQLogo.png", width=200)
    st.title("Welcome to FinQ! 👋")

    # This is a placeholder for the Google Sign-In button.
    # In a real app, this would be a more sophisticated implementation.
    st.write("Please sign in with your Google account.")
    
    # We will use a simple text input for the user to enter their email.
    # This simulates getting the user's email from the OAuth provider.
    email = st.text_input("Enter your Google email to sign in:")
    
    if st.button("Sign in with Google"):
        if email:
            login_user(email)
            st.experimental_rerun()
        else:
            st.warning("Please enter your email.")

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
