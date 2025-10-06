import yfinance as yf
from datetime import datetime, timedelta

def get_stock_data(symbol: str, days: int = 30) -> dict:
    """
    Fetch OHLCV (Open, High, Low, Close, Volume) for the past `days`.
    Returns dict with symbol and data list.
    """
    try:
        end = datetime.today()
        start = end - timedelta(days=days)

        ticker = yf.Ticker(symbol)
        hist = ticker.history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))

        if hist.empty:
            return {"symbol": symbol, "data": [], "error": "No data found"}

        # Clean and convert to JSON
        data = []
        for date, row in hist.iterrows():
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"])
            })

        return {"symbol": symbol, "data": data}

    except Exception as e:
        return {"symbol": symbol, "error": str(e)}
