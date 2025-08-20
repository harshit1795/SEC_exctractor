import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from components.shared import hide_default_sidebar

def render_login_form():
    """Renders the login form using streamlit-authenticator."""
    hide_default_sidebar()

    # Display logo
    try:
        st.image("FInQLogo.png", width=200)
    except:
        st.title("📈 FinQ")

    st.title("Welcome to FinQ")
    st.markdown("### Financial Intelligence & Analytics Platform")

    # Load configuration from a YAML file
    try:
        with open('config.yaml') as file:
            config = yaml.load(file, Loader=SafeLoader)
    except FileNotFoundError:
        st.error("`config.yaml` not found. Please create the configuration file.")
        st.stop()


    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    # Render the login widget
    name, authentication_status, username = authenticator.login('main')

    if st.session_state["authentication_status"]:
        st.session_state["user"] = username
        st.session_state["logged_in"] = True
        st.session_state["user_name"] = name
        st.session_state["authenticator"] = authenticator
        st.rerun()
    elif st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')

    # Add a registration form
    try:
        if authenticator.register_user('Register user', preauthorization=False):
            st.success('User registered successfully')
            # Save the updated config
            with open('config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
    except Exception as e:
        st.error(e)