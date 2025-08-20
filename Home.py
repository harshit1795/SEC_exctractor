import streamlit as st
from components.shared import render_sidebar, hide_default_sidebar
from pages import Dashboard, Financial_Health_Monitoring, Nexus, Settings
from login import render_login_form

# --- Page Configuration ---
st.set_page_config(page_title="FinQ", page_icon="📈", layout="wide")
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css" integrity="sha512-xh6O/CkQoPOWDdYTDqeRdPCVd1SpvCA9XXcUnZS2FmJNp1coAFzvtCN9BmamE+4aHK8yyUHUSCcJHgXloTyT2A==" crossorigin="anonymous" referrerpolicy="no-referrer" />', unsafe_allow_html=True)

# --- Authentication ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        render_login_form()
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