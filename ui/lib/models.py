from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class NewsItem(BaseModel):
    title: str
    url: Optional[str] = None
    source: Optional[str] = None
    published_at: Optional[str] = None
    summary: Optional[str] = None
    sentiment: Optional[float] = None

class Decision(BaseModel):
    action: str
    confidence: Optional[float] = None
    reason: Optional[str] = None

class AgentResponse(BaseModel):
    symbol: Optional[str] = None
    news: Optional[List[NewsItem]] = None
    sentiment: Optional[Dict[str, float]] = None  # e.g. {"pos":0.3,"neg":0.2,"neu":0.5,"score":0.1}
    indicators: Optional[Dict[str, Any]] = None   # e.g. latest SMA/EMA/RSI
    equity: Optional[Dict[str, Any]] = None       # list/records of price rows
    decision: Optional[Decision] = None
    raw: Dict[str, Any] = Field(default_factory=dict)
