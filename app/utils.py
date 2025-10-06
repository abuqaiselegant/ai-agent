from datetime import datetime
from fastapi import HTTPException, status

# In-memory request counter
user_requests = {}  # { "username": {"date": <date>, "count": int} }

def rate_limiter(user: str, limit: int = 30):
    """Simple per-day request limiter for each user."""
    today = datetime.utcnow().date()

    # First request of the day → initialize
    if user not in user_requests:
        user_requests[user] = {"date": today, "count": 1}
        return

    # If stored date is not today → reset counter
    if user_requests[user]["date"] != today:
        user_requests[user] = {"date": today, "count": 1}
        return

    # Increment counter
    user_requests[user]["count"] += 1

    # If limit exceeded(30) → raise 429
    if user_requests[user]["count"] > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded ({limit} requests/day). Please try again tomorrow."
        )
