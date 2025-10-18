<<<<<<< HEAD
# AI Agent - Trading Insights

AI-powered market analysis and trading insights application.

## Quick Start

### Local Development (Recommended)

```bash
# Clone and setup
cd ai-agent
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -U pip
pip install -r requirements.txt
pip install -r ui/requirements.txt
pip install -r app/requirements.txt

# Make backend starter executable
chmod +x tools/start_backend.py

# Run the app
streamlit run ui/app.py
```

The app will open at `http://localhost:8501`

### Docker (Alternative)

```bash
docker-compose up --build
```

- UI: `http://localhost:8501`
- API: `http://localhost:8000`

## Features

- **Single-page minimalist UI** - Clean, flat design with light/dark theme toggle
- **Auto-start backend** - Backend starts automatically when needed
- **Theme toggle** - Switch between light and dark modes
- **Custom branding** - Header logo/banner support
- **Real-time analysis** - Stock data, news, sentiment, technical indicators
- **Trading signals** - AI-powered buy/sell/hold recommendations
- **Interactive charts** - Price charts with RSI and technical indicators

## Usage

1. **Select theme** - Use sidebar to toggle between light/dark mode
2. **Enter a stock symbol** - e.g., TSLA, AAPL, GOOGL
3. **Select analysis options** - News, Equity, Sentiment, Indicators, Decision
4. **Click "Analyze"** - AI agent runs analysis
5. **View results** - Summary, Chart, News, Sentiment, Indicators, JSON tabs

## Architecture

- **Frontend**: Streamlit single-page app (ui/app.py)
- **Backend**: FastAPI (app/main.py)
- **Auto-start**: Auto-start script (tools/start_backend.py)

## Project Structure

```
ai-agent/
├── app/                    # FastAPI backend
│   ├── main.py            # API routes
│   ├── services/          # Business logic
│   └── requirements.txt
├── ui/                    # Streamlit frontend
│   ├── app.py            # Main app (single-page)
│   ├── components/       # UI components
│   ├── lib/              # API client & utilities
│   ├── resources/        # Static assets (banner)
│   └── requirements.txt
├── tools/                 # Helper scripts
│   └── start_backend.py  # Backend auto-start
├── docker-compose.yml    # Docker setup
└── README.md
```

## Configuration

Set environment variables in `.env`:

```env
API_BASE_URL=http://127.0.0.1:8000
CORS_ORIGINS=http://localhost:8501,http://127.0.0.1:8501
```

## Theme Customization

The app features a minimalist design with theme toggle support:

### Color Palette

**Dark Theme:**
- Background: `#0a0e1a` (deep navy)
- Primary: `#2563eb` (blue)
- Text: `#ffffff`, `#f1f5f9`, `#cbd5e1`

**Light Theme:**
- Background: `#f8fafc` (off-white)
- Primary: `#2563eb` (blue)
- Text: `#0f172a`, `#1e293b`, `#475569`

### Custom Banner

Add your banner image to `ui/resources/images/`:
- `banner.png` or `banner.jpg` - Default banner
- `banner_dark.png` - Dark theme variant (optional)
- `banner_light.png` - Light theme variant (optional)

Recommended size: 400x100px or square 200x200px

## Recent Updates (October 2025)

✨ **New Features:**
- Minimalist theme with light/dark mode toggle
- Single-page architecture (consolidated from multi-page)
- Auto-start backend functionality
- Custom header logo/banner support
- Clean flat UI design (removed gradients)

🧹 **Cleanup:**
- Removed 15+ unused files and backups
- Eliminated duplicate code and components
- Cleaned up cache files and old documentation
- Streamlined project structure

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - See LICENSE file for details
=======
# 🤖 AI Agent - Trading Insights

AI-powered market analysis with **news**, **prices**, **sentiment**, **indicators**, and **Buy/Hold/Sell** decisions.  
Built with FastAPI + LangGraph + Streamlit. Fully Dockerized with CI/CD to GHCR and deployed on Render.

- **API (Render):** https://ai-agent-3yvo.onrender.com  
- **UI (Render):** https://ai-agent-ui-ojg6.onrender.com

---

## ✨ Features

- **Single-page minimalist UI** - Clean, flat design with light/dark theme toggle
- **Auto-start backend** - Backend starts automatically when needed
- **Theme toggle** - Switch between light and dark modes  
- **Custom branding** - Header logo/banner support
- **Real-time analysis** - Stock data, news, sentiment, technical indicators
- **Trading signals** - AI-powered buy/sell/hold recommendations with T+1/T+5 horizons
- **Interactive charts** - Price charts with RSI and technical indicators

## 🚀 Quick Start

### Local Development (Recommended)

```bash
# Clone and setup
cd ai-agent
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -U pip
pip install -r requirements.txt
pip install -r ui/requirements.txt
pip install -r app/requirements.txt

# Make backend starter executable
chmod +x tools/start_backend.py

# Run the app
streamlit run ui/app.py
```

The app will open at `http://localhost:8501`

### Docker (Alternative)

```bash
# Development
docker-compose up --build

# Production (uses GHCR images)
docker-compose -f docker-compose.prod.yml up
```

- UI: `http://localhost:8501`
- API: `http://localhost:8000`

## 📖 How It Works

1) **UI → API call**  
   Enter a ticker and choose modules (News, Equity, Sentiment, Indicators, Decision). The UI hits:
   ```
   GET /agent/{symbol}?news=1&equity=1&sentiment=1&indicators=1&decision=1
   ```

2) **Agent orchestration (LangGraph)**  
   The API runs a graph where each node is optional:
   - **News** → fetch recent headlines (`NEWS_API_KEY`)
   - **Equity** → fetch OHLCV prices (yfinance)
   - **Sentiment** → score headlines (OpenAI or local fallback)
   - **Indicators** → TA metrics (RSI, MACD, SMA/EMA, VWAP, volatility)
   - **Decision** → combine sentiment + indicators → **T+1 / T+5 Buy/Hold/Sell** with confidence

3) **Unified JSON → UI render**  
   API returns complete analysis data, displayed in tabs: Summary, Chart, News, Sentiment, Indicators, JSON

## 🎯 Usage

1. **Select theme** - Use sidebar to toggle between light/dark mode
2. **Enter a stock symbol** - e.g., TSLA, AAPL, GOOGL
3. **Select analysis options** - News, Equity, Sentiment, Indicators, Decision
4. **Click "Analyze"** - AI agent runs analysis
5. **View results** - Summary, Chart, News, Sentiment, Indicators, JSON tabs

## 🏗️ Architecture

- **Frontend**: Streamlit single-page app (ui/app.py)
- **Backend**: FastAPI with LangGraph orchestration (app/main.py)
- **Auto-start**: Backend auto-start script (tools/start_backend.py)

## 📁 Project Structure

```
ai-agent/
├── app/                    # FastAPI backend
│   ├── main.py            # FastAPI app + CORS + /health
│   ├── routes.py          # /agent/{symbol} endpoint
│   ├── services/          # Business logic
│   │   ├── orchestrator.py    # LangGraph agent
│   │   ├── news_tool.py       # News fetching
│   │   ├── equity_tool.py     # Price data
│   │   ├── sentiment_tool.py  # Sentiment analysis
│   │   ├── indicators.py      # Technical indicators
│   │   └── decision_tool.py   # Trading signals
│   └── requirements.txt
├── ui/                    # Streamlit frontend
│   ├── app.py            # Main app (single-page, 400 lines)
│   ├── components/       # UI components (news_table, summary)
│   ├── lib/              # API client & utilities
│   ├── resources/        # Static assets (banner)
│   └── requirements.txt
├── tools/                 # Helper scripts
│   └── start_backend.py  # Backend auto-start
├── docker-compose.yml    # Dev: build from source
├── docker-compose.prod.yml    # Prod: pull from GHCR
├── .github/workflows/docker.yml    # CI/CD pipeline
└── README.md
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`):

```env
# Backend (API)
OPENAI_API_KEY=your-openai-key
NEWS_API_KEY=your-news-api-key
CORS_ORIGINS=http://localhost:8501,http://127.0.0.1:8501

# Frontend (UI)
API_BASE_URL=http://127.0.0.1:8000
```

### Render Deployment

**UI environment:**
```
API_BASE_URL=https://ai-agent-3yvo.onrender.com
```

**API environment:**
```
CORS_ORIGINS=https://ai-agent-ui-ojg6.onrender.com
OPENAI_API_KEY=your-key
NEWS_API_KEY=your-key
```

### Troubleshooting

- **CORS error** → API `CORS_ORIGINS` must equal the UI URL; UI `API_BASE_URL` must point to API URL
- **Streamlit secrets.toml error** → Not needed in Docker/Render; UI reads env (`API_BASE_URL`) first

## 🎨 Theme Customization

The app features a minimalist design with theme toggle support:

### Color Palette

**Dark Theme:**
- Background: `#0a0e1a` (deep navy)
- Primary: `#2563eb` (blue)
- Text: `#ffffff`, `#f1f5f9`, `#cbd5e1`

**Light Theme:**
- Background: `#f8fafc` (off-white)
- Primary: `#2563eb` (blue)
- Text: `#0f172a`, `#1e293b`, `#475569`

### Custom Banner

Add your banner image to `ui/resources/images/`:
- `banner.png` or `banner.jpg` - Default banner
- `banner_dark.png` - Dark theme variant (optional)
- `banner_light.png` - Light theme variant (optional)

Recommended size: 400x100px or square 200x200px

## 📝 Recent Updates (October 2025)

✨ **New Features:**
- Minimalist theme with light/dark mode toggle
- Single-page architecture (consolidated from multi-page)
- Auto-start backend functionality
- Custom header logo/banner support
- Clean flat UI design (removed gradients)

🧹 **Cleanup:**
- Removed 20+ unused files and backups
- Eliminated duplicate code and components
- Cleaned up cache files and old documentation
- Streamlined project structure (32% file reduction)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT © 2025 — abuqaiselegant










>>>>>>> a58f2a6b2bd1a023dfb83ab4feaeb1989ec9b426
