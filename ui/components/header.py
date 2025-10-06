import streamlit as st

def app_header():
    st.set_page_config(page_title="AI Agent Dashboard", page_icon="🤖", layout="wide")
    st.title("🤖 AI Agent — Streamlit UI")
    st.caption("FastAPI + LangGraph Agent • News • Equity • Sentiment • Indicators • Decision")
