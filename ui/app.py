import re
import streamlit as st
import pandas as pd
import subprocess
import sys
import os
import time
from pathlib import Path
from lib.state import get_api_client, ensure_login_if_needed
from lib.viz import equity_to_df, price_chart, rsi_chart
from components.summary import decision_badge, sentiment_summary
from components.news_table import render_news

# PAGE CONFIG
st.set_page_config(
    page_title="AI Trading Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# THEME MANAGEMENT
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

def get_theme_styles(theme='dark'):
    if theme == 'dark':
        return """
        <style>
            .stApp { background-color: #0a0e1a; }
            .main .block-container { padding-top: 1.5rem; max-width: 1400px; }
            h1 { color: #ffffff; font-weight: 600; font-size: 2.2rem !important; }
            h2, h3, h4, h5 { color: #f1f5f9; font-weight: 600; }
            .stApp p, .stMarkdown { color: #94a3b8; }
            
            .stButton > button[kind="primary"] {
                background-color: #2563eb; color: white; border: none;
                font-weight: 600; border-radius: 8px; padding: 0.65rem 2.5rem;
            }
            .stButton > button[kind="primary"]:hover {
                background-color: #1d4ed8; transform: translateY(-1px);
            }
            .stButton > button {
                background-color: transparent; color: #cbd5e1; border: 1px solid #334155;
                font-weight: 500; border-radius: 6px;
            }
            .stButton > button:hover {
                background-color: #1e293b; color: #f1f5f9; border-color: #475569;
            }
            
            .stTextInput > div > div > input {
                background-color: #1e293b; color: #f1f5f9; border: 1px solid #334155;
                border-radius: 8px; padding: 0.7rem 1rem;
            }
            .stTextInput > div > div > input:focus {
                border-color: #2563eb; box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
            }
            .stTextInput > label { color: #cbd5e1 !important; font-weight: 500 !important; }
            
            .stCheckbox {
                background-color: #1e293b; padding: 0.7rem 1rem;
                border-radius: 6px; border: 1px solid #334155;
            }
            .stCheckbox:hover { background-color: #334155; border-color: #475569; }
            .stCheckbox > label { color: #cbd5e1 !important; font-weight: 500 !important; }
            
            .stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid #334155; }
            .stTabs [data-baseweb="tab"] {
                background-color: transparent; color: #94a3b8; border: none;
                border-bottom: 2px solid transparent; padding: 10px 20px;
            }
            .stTabs [data-baseweb="tab"]:hover { color: #cbd5e1; background-color: #1e293b; }
            .stTabs [aria-selected="true"] {
                color: #2563eb !important; border-bottom-color: #2563eb !important;
            }
            
            .stSuccess { background-color: #064e3b; border-left: 3px solid #10b981; color: #a7f3d0; }
            .stError { background-color: #7f1d1d; border-left: 3px solid #ef4444; color: #fca5a5; }
            .stInfo { background-color: #1e3a8a; border-left: 3px solid #3b82f6; color: #93c5fd; }
            
            hr { border-color: #1e293b; margin: 1.5rem 0; }
            section[data-testid="stSidebar"] { background-color: #0f172a; border-right: 1px solid #1e293b; }
        </style>
        """
    else:
        return """
        <style>
            .stApp { background-color: #f8fafc; }
            .main .block-container { padding-top: 1.5rem; max-width: 1400px; }
            h1 { color: #0f172a !important; font-weight: 600; font-size: 2.2rem !important; }
            h2, h3, h4, h5 { color: #1e293b; font-weight: 600; }
            .stApp p, .stMarkdown { color: #64748b; }
            
            .stButton > button[kind="primary"] {
                background-color: #2563eb; color: white; border: none;
                font-weight: 600; border-radius: 8px; padding: 0.65rem 2.5rem;
            }
            .stButton > button[kind="primary"]:hover {
                background-color: #1d4ed8; transform: translateY(-1px);
            }
            .stButton > button {
                background-color: white; color: #475569; border: 1px solid #cbd5e1;
                font-weight: 500; border-radius: 6px;
            }
            .stButton > button:hover {
                background-color: #f1f5f9; color: #1e293b; border-color: #94a3b8;
            }
            
            .stTextInput > div > div > input {
                background-color: white; color: #1e293b; border: 1px solid #cbd5e1;
                border-radius: 8px; padding: 0.7rem 1rem;
            }
            .stTextInput > div > div > input:focus {
                border-color: #2563eb; box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
            }
            .stTextInput > label { color: #475569 !important; font-weight: 500 !important; }
            
            .stCheckbox {
                background-color: white; padding: 0.7rem 1rem;
                border-radius: 6px; border: 1px solid #e2e8f0;
            }
            .stCheckbox:hover { background-color: #f8fafc; border-color: #cbd5e1; }
            .stCheckbox > label { color: #475569 !important; font-weight: 500 !important; }
            
            .stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid #e2e8f0; }
            .stTabs [data-baseweb="tab"] {
                background-color: transparent; color: #64748b; border: none;
                border-bottom: 2px solid transparent; padding: 10px 20px;
            }
            .stTabs [data-baseweb="tab"]:hover { color: #475569; background-color: #f8fafc; }
            .stTabs [aria-selected="true"] {
                color: #2563eb !important; border-bottom-color: #2563eb !important;
            }
            
            .stSuccess { background-color: #d1fae5; border-left: 3px solid #10b981; color: #065f46; }
            .stError { background-color: #fee2e2; border-left: 3px solid #ef4444; color: #991b1b; }
            .stInfo { background-color: #dbeafe; border-left: 3px solid #3b82f6; color: #1e40af; }
            
            hr { border-color: #e2e8f0; margin: 1.5rem 0; }
            section[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
        </style>
        """

# Apply theme
st.markdown(get_theme_styles(st.session_state.theme), unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    current_theme = st.session_state.theme
    if st.button(f"Switch to {'☀️ Light' if current_theme == 'dark' else '🌙 Dark'} Theme", key="theme_toggle"):
        toggle_theme()
        st.rerun()
    st.markdown(f"**Current:** {'🌙 Dark Mode' if current_theme == 'dark' else '☀️ Light Mode'}")
    st.markdown("---")
    st.markdown("### 📊 About")
    st.markdown("AI-powered trading analysis with real-time market intelligence.")

# Banner
def load_banner():
    resources_path = Path(__file__).parent / "resources" / "images"
    theme = st.session_state.theme
    banner_files = [f"banner_{theme}.png", f"banner_{theme}.jpg", "banner.png", "banner.jpg"]
    for banner_file in banner_files:
        banner_path = resources_path / banner_file
        if banner_path.exists():
            return str(banner_path)
    return None

# HELPERS
HORIZON_RE = re.compile(r"t\+(\d+)", re.IGNORECASE)

@st.cache_data(ttl=300, show_spinner=False)
def _fetch_equity_df(symbol: str):
    client = get_api_client()
    ensure_login_if_needed()
    try:
        data = client.get_equity(symbol)
    except Exception:
        data = {}
    return equity_to_df(data or {})

def _is_horizon_key(k: str) -> bool:
    return isinstance(k, str) and (HORIZON_RE.search(k) is not None or "horizon" in k.lower())

def _horizon_sort_key(k: str) -> int:
    m = HORIZON_RE.search(k)
    return int(m.group(1)) if m else 999

def _deep_find_decision(obj, path=None):
    if path is None:
        path = []
    if isinstance(obj, dict):
        if "decision" in obj:
            return obj["decision"], path + ["decision"]
        if any(k in obj for k in ("signal", "action", "recommendation", "verdict", "call")):
            return obj, path
        for k, v in obj.items():
            found, p = _deep_find_decision(v, path + [k])
            if found is not None:
                return found, p
    elif isinstance(obj, (list, tuple)):
        for i, it in enumerate(obj):
            found, p = _deep_find_decision(it, path + [f"[{i}]"])
            if found is not None:
                return found, p
    return None, None

def _unwrap_decision_container(dec):
    if not isinstance(dec, dict):
        return dec
    if "decision" in dec and isinstance(dec["decision"], dict):
        dec = dec["decision"]
    if "horizons" in dec and isinstance(dec["horizons"], dict):
        dec = dec["horizons"]
    return dec

def _sentiment_articles(s: dict | None):
    if not isinstance(s, dict):
        return None
    return s.get("articles") or s.get("items") or s.get("per_article")

def ensure_backend_running(timeout: int = 40):
    client = get_api_client()
    try:
        client.health()
        return True
    except Exception:
        pass
    
    tools_path = os.path.join(os.path.dirname(__file__), '..', 'tools', 'start_backend.py')
    tools_path = os.path.normpath(tools_path)
    
    try:
        subprocess.run([sys.executable, tools_path], stdout=subprocess.PIPE,
                      stderr=subprocess.STDOUT, text=True, timeout=50)
    except Exception:
        pass
    
    waited = 0
    interval = 1
    while waited < timeout:
        try:
            client.health()
            return True
        except Exception:
            time.sleep(interval)
            waited += interval
    return False

@st.cache_data(ttl=300, show_spinner=False)
def call_agent(symbol: str, params: dict):
    client = get_api_client()
    ensure_login_if_needed()
    if "decision" in params:
        v = params["decision"]
        for alias in ("do_decision", "make_decision", "signal", "trade_decision"):
            params.setdefault(alias, v)
    data = client.run_agent(symbol, **params)
    return data

# MAIN APP
def main():
    # Header with logo
    banner_path = load_banner()
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        if banner_path:
            st.image(banner_path, width=100)
        else:
            st.write("🤖")
    with col2:
        st.title("AI Trading Agent")
        st.caption("Real-time market intelligence")
    with col3:
        if st.button("🗑️ Clear"):
            st.cache_data.clear()
            st.toast("✅ Cleared!", icon="✨")
    
    st.markdown("---")
    
    # Input
    symbol = st.text_input("📊 Symbol", value="TSLA", placeholder="AAPL, GOOGL, TSLA...")
    
    # Options
    st.markdown("##### Analysis Options")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        do_news = st.checkbox("📰 News", value=True)
    with col2:
        do_equity = st.checkbox("📈 Equity", value=True)
    with col3:
        do_sent = st.checkbox("💭 Sentiment", value=True)
    with col4:
        do_ind = st.checkbox("📊 Indicators", value=True)
    with col5:
        do_decision = st.checkbox("🎯 Decision", value=True)
    
    st.markdown("---")
    
    # Analyze
    if st.button("🚀 Analyze", use_container_width=True, type="primary"):
        if not symbol.strip():
            st.warning("Please enter a symbol")
            return
        
        with st.spinner("Starting..."):
            if not ensure_backend_running():
                st.error("Could not start backend")
                return
        
        params = {
            "news": int(do_news),
            "equity": int(do_equity),
            "sentiment": int(do_sent),
            "indicators": int(do_ind),
            "decision": int(do_decision),
        }
        
        with st.spinner("Analyzing..."):
            try:
                data = call_agent(symbol.strip(), params)
            except Exception as e:
                st.error(f"Failed: {e}")
                return
        
        st.success("✅ Complete!")
        st.markdown("---")
        
        # Results
        t_summary, t_chart, t_news, t_sent, t_ind, t_json = st.tabs(
            ["Summary", "Chart", "News", "Sentiment", "Indicators", "JSON"]
        )
        
        with t_summary:
            dec_container, _ = _deep_find_decision(data)
            dec_container = _unwrap_decision_container(dec_container)
            
            left, right = st.columns(2)
            
            with left:
                st.subheader("🎯 Decision")
                if isinstance(dec_container, dict):
                    if any(k in dec_container for k in ("signal", "action", "recommendation")):
                        decision_badge(dec_container)
                    else:
                        horizon_keys = [k for k in dec_container.keys() if _is_horizon_key(k)]
                        if horizon_keys:
                            for hk in sorted(horizon_keys, key=_horizon_sort_key):
                                st.caption(f"**{hk.upper()}**")
                                decision_badge(dec_container.get(hk))
                        else:
                            st.info("No decision")
                else:
                    st.info("No decision")
            
            with right:
                st.subheader("💭 Sentiment")
                sentiment_summary(data.get("sentiment"))
        
        with t_chart:
            df = equity_to_df(data.get("equity") or data)
            if df.empty:
                df = _fetch_equity_df(symbol.strip())
            
            if df.empty:
                st.info("No equity data")
            else:
                st.plotly_chart(price_chart(df), use_container_width=True)
                if "rsi" in df.columns:
                    st.plotly_chart(rsi_chart(df), use_container_width=True)
                with st.expander("Data"):
                    st.dataframe(df.tail(100), use_container_width=True)
        
        with t_news:
            render_news(data.get("news"))
        
        with t_sent:
            s = data.get("sentiment") or {}
            sentiment_summary(s)
            articles = _sentiment_articles(s)
            if articles:
                st.dataframe(pd.DataFrame(articles), use_container_width=True)
        
        with t_ind:
            ind = data.get("indicators") or {}
            if not ind:
                st.info("No indicators")
            else:
                st.json(ind)
        
        with t_json:
            st.json(data)

if __name__ == "__main__":
    main()
