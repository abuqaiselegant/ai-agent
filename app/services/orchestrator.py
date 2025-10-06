from langgraph.graph import StateGraph, END
from typing import TypedDict

from app.services.news_tool import get_latest_news
from app.services.sentiment_tool import analyze_sentiment, aggregate_sentiment
from app.services.equity_tool import get_stock_data
from app.services.indicators import compute_indicators
from app.services.decision_tool import hybrid_decision


# ---- Define State ----
class AgentState(TypedDict):
    symbol: str
    news: list
    sentiment: dict
    stock_data: dict
    indicators: dict
    decision: dict


# ---- Define Nodes ----
def fetch_news(state: AgentState):
    news = get_latest_news(state["symbol"], limit=3)
    return {"news": news}

def analyze_news(state: AgentState):
    headlines = [n["title"] for n in state["news"]]
    results = analyze_sentiment(headlines)
    overall = aggregate_sentiment(results)
    return {"sentiment": overall}

def fetch_equity(state: AgentState):
    stock_data = get_stock_data(state["symbol"], days=60)
    return {"stock_data": stock_data}

def compute_tech(state: AgentState):
    indicators = compute_indicators(state["stock_data"], advanced=True)["indicators"]
    return {"indicators": indicators}

def make_decision(state: AgentState):
    decision = hybrid_decision(state["symbol"], state["sentiment"], state["indicators"])
    return {"decision": decision}


# ---- Build Workflow ----
def build_agent_workflow():
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("fetch_news", fetch_news)
    graph.add_node("analyze_news", analyze_news)
    graph.add_node("fetch_equity", fetch_equity)
    graph.add_node("compute_tech", compute_tech)
    graph.add_node("make_decision", make_decision)

    # Define flow
    graph.add_edge("fetch_news", "analyze_news")
    graph.add_edge("analyze_news", "fetch_equity")
    graph.add_edge("fetch_equity", "compute_tech")
    graph.add_edge("compute_tech", "make_decision")
    graph.add_edge("make_decision", END)

    graph.set_entry_point("fetch_news")
    return graph.compile()
