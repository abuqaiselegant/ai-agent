import requests
from datetime import datetime
from app.services import config

BASE_URL = "https://newsapi.org/v2/everything"

def get_latest_news(symbol: str, limit: int = 5) -> list[dict]:
    """
    Fetch latest financial news for a given stock symbol.
    Returns a list of dicts with title, date, url.
    """

    if not config.NEWS_API_KEY:
        raise ValueError("NEWS_API_KEY not found. Please set it in .env")

    params = {
        "q": symbol,            # search query
        "sortBy": "publishedAt",# order by recency
        "pageSize": limit,      # number of articles
        "apiKey": config.NEWS_API_KEY
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        raise RuntimeError(f"News API error: {response.status_code} - {response.text}")

    data = response.json()
    articles = data.get("articles", [])

    # Clean and format output
    results = []
    for a in articles:
        results.append({
            "title": a["title"],
            "publishedAt": a["publishedAt"],
            "url": a["url"],
            "source": a["source"]["name"]
        })

    return results
