import streamlit as st

def hide_default_sidebar():
    st.markdown("""
        <style>
            div[data-testid="stSidebarNav"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)
