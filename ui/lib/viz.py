import math
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---------------- parsing helpers ----------------

PRICE_KEYS = {"open", "high", "low", "close", "adj_close", "price"}
TIME_KEYS  = {"datetime", "timestamp", "date", "time"}
VOL_KEYS   = {"volume", "vol"}

def _maybe_epoch_to_datetime(x):
    """Handle epoch seconds/millis or ISO strings."""
    # numeric?
    try:
        fx = float(x)
        # heuristics: ms vs s
        if fx > 1e12:   # nanoseconds, unlikely from APIs; downscale
            return pd.to_datetime(fx, unit="ns", utc=True)
        if fx > 1e10:   # milliseconds
            return pd.to_datetime(fx, unit="ms", utc=True)
        if fx > 1e8:    # seconds
            return pd.to_datetime(fx, unit="s", utc=True)
    except Exception:
        pass
    # string or already datetime-like
    return pd.to_datetime(x, utc=True, errors="coerce")

def _lower_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    # keep original for safety, also provide lower alias columns
    lower = {c: c.lower() for c in df.columns}
    df.rename(columns=lower, inplace=True)
    # common renames
    renames = {
        "adj_close": "close",
        "adjusted_close": "close",
        "price": "close",
        "ts": "timestamp",
    }
    for k, v in renames.items():
        if k in df.columns and v not in df.columns:
            df.rename(columns={k: v}, inplace=True)
    # indicators to conventional lower names
    for k in list(df.columns):
        lk = k.lower()
        if lk != k:
            if lk not in df.columns:
                df.rename(columns={k: lk}, inplace=True)
    return df

def _extract_records(obj):
    """
    Try very hard to get a list[dict] of rows from many shapes:
    - {'equity': {'data': [...]}}
    - {'equity': [...]}
    - {'prices': [...]}, {'data': [...]}
    - directly a list[dict]
    - nested under {'result'|'agent'|'output'|'payload'|'response'}
    """
    if obj is None:
        return None

    # direct list
    if isinstance(obj, list) and (len(obj) == 0 or isinstance(obj[0], dict)):
        return obj

    # dict with obvious arrays
    if isinstance(obj, dict):
        for key in ("equity", "prices", "price", "series", "data", "timeseries", "time_series"):
            val = obj.get(key)
            if isinstance(val, list):
                return val
            if isinstance(val, dict) and isinstance(val.get("data"), list):
                return val.get("data")

        # search common containers
        for c in ("result", "agent", "output", "payload", "response"):
            v = obj.get(c)
            rec = _extract_records(v)
            if rec is not None:
                return rec

    return None

def equity_to_df(equity_obj: dict | list | None) -> pd.DataFrame:
    """
    Convert backend 'equity' payloads into a canonical DataFrame with:
    - datetime (UTC), open/high/low/close, volume (if present)
    - common indicators preserved (sma, ema, vwap, rsi, macd, macd_signal, bb_* ...)
    Robust to many shapes and column namings.
    """
    records = _extract_records(equity_obj)
    if not records:
        # As a last resort, if the input already looks like rows in a dict
        if isinstance(equity_obj, dict) and "data" in equity_obj and isinstance(equity_obj["data"], list):
            records = equity_obj["data"]
        else:
            return pd.DataFrame()

    df = pd.DataFrame(records)
    if df.empty:
        return df

    df = _lower_cols(df)

    # ensure a datetime column
    dt_col = None
    for cand in TIME_KEYS:
        if cand in df.columns:
            dt_col = cand
            break
    if dt_col is None:
        # some APIs give index as time
        if not df.index.empty and not isinstance(df.index, pd.RangeIndex):
            df = df.reset_index(names="datetime")
            dt_col = "datetime"

    if dt_col is None:
        # no time → cannot chart meaningfully
        return pd.DataFrame()

    # parse datetime
    df["datetime"] = df[dt_col].apply(_maybe_epoch_to_datetime)
    df.dropna(subset=["datetime"], inplace=True)

    # numeric coercions
    for col in set(df.columns) & (PRICE_KEYS | VOL_KEYS | {"sma","ema","vwap","rsi","macd","macd_signal","bb_upper","bb_lower"}):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # prefer OHLC; close fallback
    has_ohlc = {"open","high","low","close"}.issubset(df.columns)
    if not has_ohlc and "close" not in df.columns:
        # sometimes 'close' lives as 'c'
        if "c" in df.columns:
            df.rename(columns={"c": "close"}, inplace=True)

    # tidy
    df = df.sort_values("datetime").drop_duplicates(subset=["datetime"]).reset_index(drop=True)

    return df

# ---------------- chart builders ----------------

def price_chart(df: pd.DataFrame):
    """
    Returns a Plotly Figure with:
    - Row 1: Candles (or Close line) + overlays (SMA/EMA/VWAP/BB)
    - Row 2: Volume bars (if available)
    With range buttons and unified hover.
    """
    if df is None or df.empty or "datetime" not in df.columns:
        return go.Figure()

    has_ohlc = {"open","high","low","close"}.issubset(df.columns)
    has_vol  = "volume" in df.columns

    fig = make_subplots(
        rows=2 if has_vol else 1, cols=1, shared_xaxes=True,
        vertical_spacing=0.03, row_heights=[0.75, 0.25] if has_vol else [1.0]
    )

    # price
    if has_ohlc:
        fig.add_trace(
            go.Candlestick(
                x=df["datetime"],
                open=df["open"], high=df["high"], low=df["low"], close=df["close"],
                name="Price"
            ),
            row=1, col=1
        )
    elif "close" in df.columns:
        fig.add_trace(
            go.Scatter(x=df["datetime"], y=df["close"], mode="lines", name="Close"),
            row=1, col=1
        )

    # overlays
    overlays = [
        ("sma", "SMA"),
        ("ema", "EMA"),
        ("vwap", "VWAP"),
        ("bb_upper", "BB Upper"),
        ("bb_lower", "BB Lower"),
        ("macd_signal", "MACD Signal"),  # if overlaid, still okay
    ]
    for key, label in overlays:
        if key in df.columns:
            fig.add_trace(
                go.Scatter(x=df["datetime"], y=df[key], mode="lines", name=label),
                row=1, col=1
            )

    # volume
    if has_vol:
        fig.add_trace(
            go.Bar(x=df["datetime"], y=df["volume"], name="Volume", opacity=0.5),
            row=2, col=1
        )

    # layout polish
    fig.update_layout(
        height=640,
        margin=dict(l=20, r=20, t=30, b=20),
        hovermode="x unified",
        xaxis=dict(
            rangeslider=dict(visible=False),
            rangeselector=dict(
                buttons=list([
                    dict(count=7,  label="1W", step="day",  stepmode="backward"),
                    dict(count=30, label="1M", step="day",  stepmode="backward"),
                    dict(count=90, label="3M", step="day",  stepmode="backward"),
                    dict(count=180,label="6M", step="day",  stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
    )
    if has_vol:
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)

    return fig

def rsi_chart(df: pd.DataFrame):
    if df is None or df.empty or "rsi" not in df.columns:
        return go.Figure()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["datetime"], y=df["rsi"], mode="lines", name="RSI"))
    fig.update_layout(
        height=220,
        margin=dict(l=20, r=20, t=30, b=20),
        yaxis=dict(range=[0, 100]),
        hovermode="x unified",
    )
    return fig
