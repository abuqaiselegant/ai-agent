import streamlit as st

# ---------- helpers ----------

def _num(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def _pick(d: dict, keys, default=None):
    for k in keys:
        if k in d:
            return d[k]
    return default

def _normalize_score(x):
    if x is None:
        return 0.0
    v = _num(x, 0.0)
    # scale 0..100 or -100..100 to -1..1 if needed
    if abs(v) > 1.0 and abs(v) <= 100.0:
        v = v / 100.0
    return max(-1.0, min(1.0, v))

def _strength_word(v: float) -> str:
    v = abs(v)
    if v < 0.2:  return "very weak"
    if v < 0.4:  return "weak"
    if v < 0.6:  return "moderate"
    if v < 0.8:  return "strong"
    return "very strong"

def _pill(text: str, kind: str = "neutral"):
    color = {"positive": "#16a34a", "negative": "#dc2626", "neutral": "#6b7280"}.get(kind, "#6b7280")
    fg = "#ffffff" if kind in ("positive", "negative") else "#e5e7eb"
    st.markdown(
        f"""
        <span style="
            padding:4px 12px; border-radius:999px;
            background-color:{color}26; border:1px solid {color}55;
            color:{fg}; font-weight:600; display:inline-block;">
            {text}
        </span>
        """,
        unsafe_allow_html=True,
    )

# ---------- sentiment ----------

def normalize_sentiment(s: dict | None):
    """
    Returns:
      {pos:0..1, neg:0..1, neu:0..1, score:-1..1, label:'Positive'|'Negative'|'Neutral'}
    Supports:
      - s['breakdown'] {positive, negative, neutral} OR top-level keys
      - score/compound/polarity/confidence
      - overall/label string
    """
    if not s or not isinstance(s, dict):
        return {"pos": 0.0, "neg": 0.0, "neu": 1.0, "score": 0.0, "label": "Neutral"}

    b = s.get("breakdown") if isinstance(s.get("breakdown"), dict) else {}
    pos = _num(_pick(s, ["pos", "positive", "Pos", "Positive"], _pick(b, ["pos", "positive"], 0)))
    neg = _num(_pick(s, ["neg", "negative", "Neg", "Negative"], _pick(b, ["neg", "negative"], 0)))
    neu = _num(_pick(s, ["neu", "neutral",  "Neu", "Neutral"],  _pick(b, ["neu", "neutral"],  0)))

    total = pos + neg + neu
    if total > 0:
        pos, neg, neu = pos/total, neg/total, neu/total
    else:
        neu = 1.0

    score = _pick(s, ["score", "compound", "polarity", "sentiment_score", "confidence"], None)
    score = _normalize_score(score) if score is not None else (pos - neg)

    label = _pick(s, ["overall", "label", "sentiment", "class", "prediction"], None)
    if isinstance(label, str):
        label = label.capitalize()
    else:
        if score > 0.05:   label = "Positive"
        elif score < -0.05: label = "Negative"
        else:               label = "Neutral"

    return {"pos": pos, "neg": neg, "neu": neu, "score": score, "label": label}

def sentiment_summary(s: dict | None):
    """User-friendly view: badge + one-line summary (no dev details)."""
    ns = normalize_sentiment(s)
    label = ns["label"]
    score = ns["score"]
    kind = label.lower()
    strength = _strength_word(score)

    _pill(label, kind)
    st.caption(f"{label} · {strength} signal · score {score:+.2f} (−1..+1)")

# ---------- decision ----------

def _normalize_conf(c):
    if c is None:
        return None
    v = _num(c, None)
    if v is None:
        return None
    if v > 1.0 and v <= 100.0:
        v = v / 100.0
    return max(0.0, min(1.0, v))

def normalize_decision(d: dict | str | None):
    if d is None or d == {}:
        return {"action": None, "confidence": None, "reason": None}

    if isinstance(d, str):
        return {"action": d.upper(), "confidence": None, "reason": None}

    action = _pick(d, ["signal", "action", "recommendation", "decision", "verdict", "call"])
    if isinstance(action, str):
        action = action.upper()
    elif action is not None:
        try:
            val = int(action)
            action = "BUY" if val > 0 else "SELL" if val < 0 else "HOLD"
        except Exception:
            action = None

    conf = _normalize_conf(_pick(d, ["confidence", "probability", "prob", "score", "strength"], None))
    reason = _pick(d, ["explanation", "reason", "rationale", "why", "text"], None)

    return {"action": action, "confidence": conf, "reason": reason}

def decision_badge(decision: dict | str | None):
    nd = normalize_decision(decision)
    action = nd.get("action")
    conf = nd.get("confidence")
    reason = nd.get("reason")

    if not action:
        st.info("No decision available.")
        return

    text = f"Decision: **{action}**"
    if conf is not None:
        text += f" · Confidence: **{conf:.2f}**"

    if action == "BUY":
        st.success(text)
    elif action == "SELL":
        st.error(text)
    else:
        st.warning(text)

    if reason:
        with st.expander("Decision rationale"):
            st.write(reason)
