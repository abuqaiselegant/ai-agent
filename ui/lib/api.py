from typing import Optional, Dict, Any
import os
import httpx
import streamlit as st
from dotenv import load_dotenv

# Load .env only if present (secrets.toml is preferred)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

def _get_secret(key: str, default: str | None = None) -> str | None:
    # Prefer environment (works in Docker), then try secrets.toml if present.
    val = os.getenv(key) or os.getenv(key.upper())
    if val:
        return val
    try:
        # st.secrets may not exist in container; wrap access
        return st.secrets.get(key, default)
    except Exception:
        return default

class APIClient:
    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        self.base_url = base_url or _get_secret("api_base_url", "http://127.0.0.1:8000")
        self.token = token

        # Single client for the session
        self._client = httpx.Client(base_url=self.base_url, timeout=60.0)

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def health(self) -> Dict[str, Any]:
        r = self._client.get("/health", headers=self._headers())
        r.raise_for_status()
        return r.json()

    def login(self, username: str, password: str) -> str:
        # Most FastAPI OAuth2 endpoints expect x-www-form-urlencoded
        payload = {"username": username, "password": password}
        headers = self._headers()
        headers["Content-Type"] = "application/x-www-form-urlencoded"

        r = self._client.post("/auth/login", data=payload, headers=headers)
        r.raise_for_status()
        data = r.json()
        token = data.get("access_token") or data.get("token")
        if not token:
            raise RuntimeError("Login succeeded but no token in response")
        self.token = token
        return token

    def run_agent(self, symbol: str, **params) -> Dict[str, Any]:
        # Mirror flags → different backend param names
        if "equity" in params:
            v = params["equity"]
            for alias in ("prices", "price", "ohlc", "hist", "time_series", "timeseries"):
                params.setdefault(alias, v)
        if "news" in params:
            v = params["news"]
            for alias in ("headlines", "articles"):
                params.setdefault(alias, v)
        if "sentiment" in params:
            v = params["sentiment"]
            for alias in ("nlp", "sent"):
                params.setdefault(alias, v)
        if "indicators" in params:
            v = params["indicators"]
            for alias in ("ta", "technical", "ind"):
                params.setdefault(alias, v)
        if "decision" in params:
            v = params["decision"]
            for alias in ("do_decision", "make_decision", "signal", "trade_decision"):
                params.setdefault(alias, v)

        r = self._client.get(f"/agent/{symbol}", params=params, headers=self._headers())
        r.raise_for_status()
        return r.json()

    def get_equity(self, symbol: str, **params) -> Dict[str, Any]:
        """
        Optional fallback if the agent response doesn't include prices.
        Tries /equity/{symbol}; if endpoint doesn't exist, returns {} quietly.
        """
        try:
            r = self._client.get(f"/equity/{symbol}", params=params, headers=self._headers())
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (404, 405):
                return {}
            raise

    def close(self) -> None:
        self._client.close()
