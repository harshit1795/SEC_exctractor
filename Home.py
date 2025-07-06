
import streamlit as st

st.set_page_config(page_title="FinQ", page_icon="📈")

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
