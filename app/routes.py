from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app import auth
from app.utils import rate_limiter


from app.services.equity_tool import get_stock_data
from app.services.news_tool import get_latest_news

from app.services.indicators import compute_indicators
from app.services.sentiment_tool import analyze_sentiment, aggregate_sentiment
from app.services.decision_tool import hybrid_decision

from app.services.orchestrator import build_agent_workflow

router = APIRouter()

# Fake in-memory user database
fake_users_db = {
    "abu": {
        "username": "abu",
        "hashed_password": auth.hash_password("password123")
    }
}


# OAuth2 scheme for FastAPI (Bearer token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Dependency: validate user from token
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = auth.decode_access_token(token)
        username: str = payload.get("sub")
        if username is None or username not in fake_users_db:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")
        return username
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


# ---- Routes ----

@router.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username/password")

    if not auth.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username/password")

    token = auth.create_access_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/ping")
def ping(user: str = Depends(get_current_user)):
    # Apply limiter before doing anything else
    rate_limiter(user)
    return {"message": f"Hello {user}, you are authenticated!"}

@router.get("/news/{symbol}")
def news(symbol: str, limit: int = 5):
    try:
        return {"symbol": symbol, "news": get_latest_news(symbol, limit)}
    except Exception as e:
        return {"error": str(e)}

@router.get("/equity/{symbol}")
def equity(symbol: str, days: int = 30):
    return get_stock_data(symbol, days)

@router.get("/indicators/{symbol}")
def indicators(symbol: str, advanced: bool = False, days: int = 60):
    stock_data = get_stock_data(symbol, days)
    return compute_indicators(stock_data, advanced=advanced)

@router.get("/sentiment/{symbol}")
def sentiment(symbol: str, model: str = "gpt-4o-mini", limit: int = 3):
    news = get_latest_news(symbol, limit)
    headlines = [n["title"] for n in news]
    results = analyze_sentiment(headlines, model=model)
    overall = aggregate_sentiment(results)
    return {"symbol": symbol, "results": results, "overall": overall}


@router.get("/decision/{symbol}")
def decision(symbol: str, advanced: bool = False, model: str = "gpt-4o-mini", limit: int = 3, days: int = 60):
    # 1. Get news + sentiment
    news = get_latest_news(symbol, limit)
    headlines = [n["title"] for n in news]
    sentiment_results = analyze_sentiment(headlines, model=model)
    sentiment_overall = aggregate_sentiment(sentiment_results)

    # 2. Get stock data + indicators
    stock_data = get_stock_data(symbol, days)
    indicators = compute_indicators(stock_data, advanced=advanced)["indicators"]

    # 3. Hybrid decision
    final = hybrid_decision(symbol, sentiment_overall, indicators, model=model)
    return final

@router.get("/agent/{symbol}")
def agent(symbol: str):
    workflow = build_agent_workflow()
    state = workflow.invoke({"symbol": symbol})
    return state

