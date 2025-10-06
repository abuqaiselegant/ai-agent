import pandas as pd
import pandas_ta as ta

def compute_indicators(stock_data: dict, advanced: bool = False) -> dict:
    """
    Compute technical indicators from OHLCV stock data.
    Basic: RSI, EMA, SMA, Volatility
    Advanced: adds MACD, Bollinger Bands, ATR, VWAP
    """
    if "data" not in stock_data or not stock_data["data"]:
        return {"error": "No stock data available"}

    df = pd.DataFrame(stock_data["data"])
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.set_index("date").sort_index()
    df = df.dropna(subset=["close", "high", "low", "volume"])

    indicators = {}

    # ---- Basic indicators ----
    df["RSI"] = ta.rsi(df["close"], length=14)
    df["EMA"] = ta.ema(df["close"], length=20)
    df["SMA"] = ta.sma(df["close"], length=20)
    df["Volatility"] = df["close"].pct_change().rolling(10).std() * 100

    indicators["RSI"] = round(df["RSI"].iloc[-1], 2)
    indicators["EMA"] = round(df["EMA"].iloc[-1], 2)
    indicators["SMA"] = round(df["SMA"].iloc[-1], 2)
    indicators["Volatility"] = round(df["Volatility"].iloc[-1], 2)

    # ---- Advanced indicators ----
    if advanced:
        macd = ta.macd(df["close"])
        bbands = ta.bbands(df["close"], length=20)
        atr = ta.atr(df["high"], df["low"], df["close"], length=14)
        vwap = ta.vwap(df["high"], df["low"], df["close"], df["volume"])

        # --- Safe access for Bollinger columns ---
        def safe_col(df, possible_names):
            for name in possible_names:
                if name in df.columns:
                    return df[name]
            return None

        upper = safe_col(bbands, ["BBU_20_2.0", "BBU_20_2", "BBU_20_2.0_Close"])
        lower = safe_col(bbands, ["BBL_20_2.0", "BBL_20_2", "BBL_20_2.0_Close"])

        indicators["MACD"] = round(macd["MACD_12_26_9"].iloc[-1], 2)
        indicators["MACD_signal"] = round(macd["MACDs_12_26_9"].iloc[-1], 2)
        indicators["ATR"] = round(atr.iloc[-1], 2)
        indicators["VWAP"] = round(vwap.iloc[-1], 2)

        if upper is not None:
            indicators["Bollinger_Upper"] = round(upper.iloc[-1], 2)
        if lower is not None:
            indicators["Bollinger_Lower"] = round(lower.iloc[-1], 2)

    return {"symbol": stock_data["symbol"], "indicators": indicators}
