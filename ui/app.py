import streamlit as st
from components.header import app_header
from lib.state import get_api_client, ensure_login_if_needed
from components.auth_box import auth_box




def main():
    app_header()
    auth_box()

    st.subheader("Connection")
    client = get_api_client()

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Ping backend /health"):
            try:
                ensure_login_if_needed()
                resp = client.health()  # requires /health on backend
                st.success(f"OK: {resp}")
            except Exception as e:
                st.error(f"Health check failed: {e}")

    st.divider()
    st.write("Use the **Agent** page (left sidebar) to run an end-to-end request.")

if __name__ == "__main__":
    main()
