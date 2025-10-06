import streamlit as st
from .api import APIClient, _get_secret

def get_api_client() -> APIClient:
    if "api_client" not in st.session_state:
        st.session_state["api_client"] = APIClient()
    return st.session_state["api_client"]

def ensure_login_if_needed():
    client = get_api_client()
    if getattr(client, "token", None):
        return
    if str(_get_secret("auto_login", "false")).lower() not in ("1","true","yes","on"):
        return
    username = _get_secret("username")
    password = _get_secret("password")
    if username and password:
        try:
            client.login(username, password)
            st.toast("Logged in to backend.", icon="✅")
        except Exception:
            # stay silent; your routes might be public in dev
            pass

