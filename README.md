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
