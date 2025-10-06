FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv

# system deps you actually use
RUN apt-get update && apt-get install -y --no-install-recommends curl \
  && rm -rf /var/lib/apt/lists/*

# deps
COPY app/requirements.txt /srv/requirements.txt
RUN pip install --no-cache-dir -r /srv/requirements.txt

# app
COPY app /srv/app

# drop privileges
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /srv
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD curl -sf http://localhost:8000/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
