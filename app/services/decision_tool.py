import json
from app.services.llm_clients import analyze_with_openai

def hybrid_decision(symbol: str, sentiment: dict, indicators: dict, model: str = "gpt-4o-mini") -> dict:
    """
    Combine sentiment + indicators into Buy/Sell/Hold decision.
    Returns t+1 and t+5 signals with confidence and explanation.
    """

    # ---- Rule-based nudges ----
    rsi = indicators.get("RSI", 50)
    ema = indicators.get("EMA", 0)
    macd = indicators.get("MACD", 0) if "MACD" in indicators else None

    rule_bias = []
    if rsi > 70:
        rule_bias.append("Overbought: leaning Sell")
    elif rsi < 30:
        rule_bias.append("Oversold: leaning Buy")
    if macd and macd > 0:
        rule_bias.append("MACD positive: leaning Buy")
    if macd and macd < 0:
        rule_bias.append("MACD negative: leaning Sell")

    # ---- Prepare LLM prompt ----
    prompt = f"""
    You are a trading signal generator.

    Stock: {symbol}
    Sentiment overall: {sentiment['overall']}
    Sentiment score: {sentiment['score']}
    Technical indicators: {indicators}
    Rule-based hints: {rule_bias}

    Task:
    - Suggest Buy / Sell / Hold for t+1 (short-term) and t+5 (medium-term).
    - Give confidence between 0 and 1.
    - Explain reasoning briefly (max 2 sentences).

    Respond ONLY in JSON format like this:
    {{
      "t+1": {{"signal": "Buy/Sell/Hold", "confidence": 0.74, "explanation": "..."}},
      "t+5": {{"signal": "Buy/Sell/Hold", "confidence": 0.65, "explanation": "..."}}
    }}
    """

    try:
        response = analyze_with_openai(prompt, model=model)
        result = json.loads(response)
    except Exception as e:
        result = {"error": str(e)}

    return {
        "symbol": symbol,
        "sentiment": sentiment,
        "indicators": indicators,
        "decision": result
    }
