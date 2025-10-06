import streamlit as st
from lib.state import get_api_client

def auth_box():
    client = get_api_client()

    with st.sidebar.expander("🔐 Login (optional)", expanded=False):
        if getattr(client, "token", None):
            st.success("Logged in")
            if st.button("Logout", key="auth_logout_btn"):
                client.token = None
                st.toast("Logged out.", icon="👋")
        else:
            u = st.text_input("Username", key="auth_user")
            p = st.text_input("Password", type="password", key="auth_pass")
            if st.button("Login", key="auth_login_btn"):
                try:
                    client.login(u, p)
                    st.success("Logged in.")
                except Exception as e:
                    st.error(f"Login failed: {e}")

