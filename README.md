# 🤖 AI Agent (FastAPI + LangGraph + Streamlit)

Pulls **news & prices**, computes **sentiment & indicators**, and outputs a **Buy/Hold/Sell** decision with confidence.  
UI is Streamlit; backend is FastAPI orchestrated with LangGraph. Fully Dockerized with CI/CD to GHCR and deployed on Render (free).

- **API (Render):** https://ai-agent-3yvo.onrender.com  
- **UI  (Render):** https://ai-agent-ui-ojg6.onrender.com

---

## How it works (quick summary)

1) **UI → API call**  
   In the Streamlit app, you enter a ticker and choose modules (News, Equity, Sentiment, Indicators, Decision). The UI hits:
GET /agent/{symbol}?news=1&equity=1&sentiment=1&indicators=1&decision=1

markdown
Copy code

2) **Agent orchestration (LangGraph)**  
The API runs a small graph where each node is optional:
- **News** → fetch recent headlines (`NEWS_API_KEY`).
- **Equity** → fetch OHLCV prices (e.g., yfinance).
- **Sentiment** → score headlines (OpenAI if `OPENAI_API_KEY` is set; local fallback if implemented).
- **Indicators** → TA like RSI, MACD, SMA/EMA, VWAP, volatility.
- **Decision** → combine sentiment + indicators → **T+1 / T+5 Buy/Hold/Sell** with confidence + explanation.

3) **Unified JSON → UI render**  
API returns:
```json
{"news": {...}, "equity": {...}, "sentiment": {...}, "indicators": {...}, "decision": {...}}
Streamlit shows a Summary (decision + sentiment), Chart, News, Sentiment, Indicators, and JSON tabs.
```

Env keys used

API: OPENAI_API_KEY, NEWS_API_KEY, CORS_ORIGINS
UI: API_BASE_URL (points to the API URL)

Project structure
```
ai-agent/
├─ app/                        # FastAPI backend (package: app)
│  ├─ services/               # news, sentiment, indicators, orchestrator, ...
│  ├─ main.py                 # FastAPI app + CORS + /health
│  ├─ routes.py               # /agent/{symbol}
│  ├─ requirements.txt
│  └─ Dockerfile
├─ ui/                         # Streamlit frontend
│  ├─ app.py                  # landing + health ping
│  ├─ pages/1_Agent.py        # Agent UI (tabs)
│  ├─ components/             # summary, news table, auth box
│  ├─ lib/                    # api client, viz, models, state
│  ├─ requirements.txt
│  └─ Dockerfile
├─ docker-compose.yml         # dev: build from source
├─ docker-compose.prod.yml    # prod: pull images from GHCR
├─ .github/workflows/docker.yml
└─ .env.example               # sample envs (copy to .env)
```


Environment
Create a .env (copy from .env.example):

# Backend (API)
OPENAI_API_KEY=your-openai-key
NEWS_API_KEY=your-news-api-key

UI env: API_BASE_URL=https://ai-agent-3yvo.onrender.com
API env: CORS_ORIGINS=https://ai-agent-ui-ojg6.onrender.com

2) UI
Runtime: Docker
Dockerfile path: ui/Dockerfile
Environment:
API_BASE_URL=https://ai-agent-3yvo.onrender.com

Troubleshooting
500 from /agent → Render API logs: most often a missing env (OPENAI_API_KEY, NEWS_API_KEY) or a Python dep (add to app/requirements.txt, push).

CORS error → API CORS_ORIGINS must equal the UI URL; UI API_BASE_URL must point to the API URL.

Streamlit secrets.toml error → not needed in Docker/Render; UI reads env (API_BASE_URL) first.

License
MIT © 2025 — abuqaiselegant






