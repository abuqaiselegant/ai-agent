import re
import streamlit as st
import pandas as pd
from lib.state import get_api_client, ensure_login_if_needed
from lib.viz import equity_to_df, price_chart, rsi_chart
from components.summary import decision_badge, sentiment_summary
from components.news_table import render_news
from components.auth_box import auth_box

st.set_page_config(page_title="Agent", page_icon="🧠", layout="wide")

# ---------------- helpers ----------------

HORIZON_RE = re.compile(r"t\+(\d+)", re.IGNORECASE)


@st.cache_data(ttl=300, show_spinner=False)
def _fetch_equity_df(symbol: str):
    client = get_api_client()
    ensure_login_if_needed()
    data = {}
    try:
        data = client.get_equity(symbol)
    except Exception:
        data = {}
    from lib.viz import equity_to_df  # safe local import
    return equity_to_df(data or {})


def _is_horizon_key(k: str) -> bool:
    return isinstance(k, str) and (HORIZON_RE.search(k) is not None or "horizon" in k.lower())

def _horizon_sort_key(k: str) -> int:
    m = HORIZON_RE.search(k)
    return int(m.group(1)) if m else 999

def _deep_find_decision(obj, path=None):
    """Deep search for a decision container anywhere; returns (container, path)."""
    if path is None:
        path = []
    if isinstance(obj, dict):
        # direct 'decision' key
        if "decision" in obj:
            return obj["decision"], path + ["decision"]
        # dict that itself looks like a decision object
        if any(k in obj for k in ("signal", "action", "recommendation", "verdict", "call")):
            return obj, path
        # recurse
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
    """
    Accepts:
      - {"t+1": {...}, "t+5": {...}}
      - {"horizons": {...}}
      - {"decision": {...}}     (extra nesting)
      - single object {"signal": "...", ...}
    Returns either a single decision object or a horizons dict.
    """
    if not isinstance(dec, dict):
        return dec
    # peel known wrappers
    if "decision" in dec and isinstance(dec["decision"], dict):
        dec = dec["decision"]
    if "horizons" in dec and isinstance(dec["horizons"], dict):
        dec = dec["horizons"]
    return dec

def _sentiment_articles(s: dict | None):
    if not isinstance(s, dict):
        return None
    return s.get("articles") or s.get("items") or s.get("per_article")

@st.cache_data(ttl=300, show_spinner=False)
def call_agent(symbol: str, params: dict):
    client = get_api_client()
    ensure_login_if_needed()   # silent if not configured
    # mirror decision flag for alternate backends
    if "decision" in params:
        v = params["decision"]
        for alias in ("do_decision", "make_decision", "signal", "trade_decision"):
            params.setdefault(alias, v)
    data = client.run_agent(symbol, **params)
    return data

auth_box()

# ---------------- page ----------------

def run():
    st.header("Agent")

    with st.sidebar:
        st.subheader("Run Settings")
        symbol = st.text_input("Ticker / Symbol", value="TSLA")

        do_news = st.toggle("News", value=True)
        do_equity = st.toggle("Equity", value=True)
        do_sent = st.toggle("Sentiment", value=True)
        do_ind = st.toggle("Indicators", value=True)
        do_decision = st.toggle("Decision", value=True)

        c1, c2 = st.columns([1, 1])
        with c1:
            run_btn = st.button("Run Agent", width="stretch")
        with c2:
            if st.button("Clear cache", width="stretch"):
                st.cache_data.clear()
                st.toast("Cache cleared.", icon="🧼")

    if run_btn:
        if not symbol.strip():
            st.warning("Please enter a symbol.")
            return

        params = {
            "news": int(do_news),
            "equity": int(do_equity),
            "sentiment": int(do_sent),
            "indicators": int(do_ind),
            "decision": int(do_decision),
        }

        with st.spinner("Calling backend agent..."):
            try:
                data = call_agent(symbol.strip(), params)
            except Exception as e:
                st.error(f"Agent call failed: {e}")
                return

        # Tabs
        t_summary, t_chart, t_news, t_sent, t_ind, t_json = st.tabs(
            ["Summary", "Chart", "News", "Sentiment", "Indicators", "JSON"]
        )

        # SUMMARY
        with t_summary:
            st.subheader("Overview")

            dec_container, dec_path = _deep_find_decision(data)
            dec_container = _unwrap_decision_container(dec_container)

            left, right = st.columns([1, 1])

            # LEFT: Decision(s)
            with left:
                if isinstance(dec_container, dict):
                    # single decision object?
                    if any(k in dec_container for k in ("signal", "action", "recommendation", "verdict", "call")):
                        decision_badge(dec_container)
                    else:
                        # horizon map
                        horizon_keys = [k for k in dec_container.keys() if _is_horizon_key(k)]
                        if horizon_keys:
                            horizon_keys = sorted(horizon_keys, key=_horizon_sort_key)
                            cols = st.columns(len(horizon_keys))
                            for i, hk in enumerate(horizon_keys):
                                with cols[i]:
                                    st.caption(f"**{hk.upper()}**")
                                    decision_badge(dec_container.get(hk))
                        else:
                            st.info("No decision available.")
                elif dec_container is not None:
                    decision_badge(dec_container)
                else:
                    st.info("No decision available.")

                with st.expander("🔎 Decision Debug", expanded=False):
                    st.write("Found at path:", " → ".join(dec_path) if dec_path else "(not found)")
                    if dec_container is not None:
                        st.json(dec_container)

            # RIGHT: Sentiment summary
            with right:
                sentiment_summary(data.get("sentiment"))

        # CHART
        with t_chart:
            # first try what the agent returned
            df = equity_to_df(data.get("equity") or data)
            if df.empty:
                # fallback: call /equity/{symbol} if available
                df = _fetch_equity_df(symbol.strip())

            if df.empty:
                st.info(
                    "No equity time-series.\n\n"
                    "Tips:\n"
                    "• Ensure the **Equity** toggle is ON.\n"
                    "• Your backend should return a list with time and price (e.g., "
                    "`datetime` + `close` or OHLC) under keys like `equity.data`, `prices`, or `data`.\n"
                    "• If your backend uses a different param name (e.g., `prices=1`), it's mirrored now."
                )
            else:
                st.plotly_chart(price_chart(df), use_container_width=True)
                if "rsi" in df.columns:
                    st.plotly_chart(rsi_chart(df), use_container_width=True)
                with st.expander("Show raw price table"):
                    st.dataframe(df.tail(250), use_container_width=True, height=360)
                # NEWS
                with t_news:
                    render_news(data.get("news"))

        # SENTIMENT
        with t_sent:
            s = data.get("sentiment") or {}
            st.write("Aggregates")
            sentiment_summary(s)

            articles = _sentiment_articles(s)
            if articles:
                st.write("Per-article scores")
                df_s = pd.DataFrame(articles)
                st.dataframe(df_s, use_container_width=True, height=420)

        # INDICATORS
        with t_ind:
            ind = data.get("indicators") or {}
            if not ind:
                st.info("No indicators.")
            else:
                st.json(ind)

        # JSON
        with t_json:
            st.json(data)

if __name__ == "__main__":
    run()
