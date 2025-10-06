import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env file from project root
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

# ----- Basic Config -----
SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# ----- External API Keys -----
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
EQUITY_API_KEY = os.getenv("EQUITY_API_KEY")

# Simple validator
def check_keys():
    missing = []
    if not NEWS_API_KEY:
        missing.append("NEWS_API_KEY")
    if not EQUITY_API_KEY:
        missing.append("EQUITY_API_KEY")
    if missing:
        print(f" Warning: Missing {', '.join(missing)} in .env")
