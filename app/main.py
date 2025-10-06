from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app import routes

# Read from env (comma-separated). Falls back to local Streamlit.
origins_str = os.getenv("CORS_ORIGINS", "http://localhost:8501,http://127.0.0.1:8501")
ALLOWED_ORIGINS = [o.strip() for o in origins_str.split(",") if o.strip()]

app = FastAPI(title="AI Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,  # keep True only if you list explicit origins (not '*')
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)

@app.get("/")
def root():
    return {"message": "AI Agent backend running!"}

@app.get("/health")
def health():
    return {"status": "ok"}
