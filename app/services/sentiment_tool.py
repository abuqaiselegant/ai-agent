import json
from app.services.llm_clients import analyze_with_openai

def analyze_sentiment(headlines: list[str], model: str = "gpt-4o-mini") -> list[dict]:
    """
    Analyze sentiment of each headline using LLM.
    Returns list of dicts with label + confidence.
    """
    results = []
    for h in headlines:
        prompt = f"""
        Classify the sentiment of this financial news headline:
        "{h}"

        Respond ONLY in JSON format:
        {{"label": "Positive/Negative/Neutral", "confidence": float between 0 and 1}}
        """

        try:
            response = analyze_with_openai(prompt, model=model)
            parsed = json.loads(response)
            results.append({"headline": h, "label": parsed["label"], "confidence": parsed["confidence"]})
        except Exception as e:
            results.append({"headline": h, "error": str(e)})

    return results


def aggregate_sentiment(results: list[dict]) -> dict:
    """
    Aggregate sentiment results into overall label + score.
    """
    if not results:
        return {"label": "Neutral", "score": 0.0}

    total_score = 0
    count = 0
    positives, negatives, neutrals = 0, 0, 0

    for r in results:
        if "confidence" in r:
            count += 1
            total_score += r["confidence"] if r["label"] == "Positive" else -r["confidence"]

            if r["label"] == "Positive": positives += 1
            elif r["label"] == "Negative": negatives += 1
            else: neutrals += 1

    avg_score = round(total_score / count, 2) if count > 0 else 0
    overall = "Positive" if avg_score > 0.2 else "Negative" if avg_score < -0.2 else "Neutral"

    return {"overall": overall, "score": avg_score, "breakdown": {"positive": positives, "negative": negatives, "neutral": neutrals}}
