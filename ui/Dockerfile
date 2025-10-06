# ui/Dockerfile  (works when build context is the repo root)
FROM python:3.12-slim

WORKDIR /ui

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl && rm -rf /var/lib/apt/lists/*

# requirements live under ui/
COPY ui/requirements.txt /ui/requirements.txt
RUN pip install --no-cache-dir -r /ui/requirements.txt

# copy the actual app
COPY ui /ui

EXPOSE 8501
ENV STREAMLIT_SERVER_HEADLESS=true STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

CMD ["streamlit","run","app.py","--server.address=0.0.0.0","--server.port=8501"]
