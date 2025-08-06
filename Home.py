import streamlit as st
from auth import show_login_ui, load_api_keys

st.set_page_config(page_title="FinQ", page_icon="📈", layout="wide")

# --- Authentication ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    show_login_ui()
    st.stop()

# --- Main Application ---
load_api_keys()

st.sidebar.success("You are logged in.")

if st.sidebar.button("Logout"):
    st.session_state["logged_in"] = False
    st.session_state["user"] = None
    st.experimental_rerun()

# --- Main Application ---


st.markdown("<style> .css-1d3f8as { display: flex; flex-direction: column; align-items: center; } </style>", unsafe_allow_html=True)
st.markdown("<style> img { display: block; margin-left: auto; margin-right: auto; } </style>", unsafe_allow_html=True)
st.image("FInQLogo.png", width=200)

st.markdown(
    """
    # Welcome to FinQ! 👋

    **FinQ is your personal financial analysis assistant.**

    This application allows you to explore and analyze financial data for S&P 500 companies.

    ### Key Features:
    *   **Financial Analysis:** Dive deep into the latest financial metrics of your chosen companies.
    *   **Financial Health Monitoring:** Keep a close eye on the financial health of your portfolio.
    *   **Nexus (Community):** Connect with other investors and share your insights.

    **👈 Select a page from the sidebar to get started!**
    """
)


