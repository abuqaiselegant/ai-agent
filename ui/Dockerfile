FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /ui

RUN apt-get update && apt-get install -y --no-install-recommends curl \
  && rm -rf /var/lib/apt/lists/*

COPY ui/requirements.txt /ui/requirements.txt
RUN pip install --no-cache-dir -r /ui/requirements.txt

COPY ui /ui

RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /ui
USER appuser

EXPOSE 8501
HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD curl -sf http://localhost:8501/ || exit 1
ENV STREAMLIT_SERVER_HEADLESS=true STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
