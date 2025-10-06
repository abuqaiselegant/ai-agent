import os
from openai import OpenAI
from app.services import config

# Load keys from env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Setup OpenAI client
openai_client = None
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_with_openai(prompt: str, model: str = "gpt-4o-mini") -> str:
    """
    Send a prompt to OpenAI LLM and return response text.
    Default: gpt-4o-mini (can change to GPT-5 later)
    """
    if not openai_client:
        raise ValueError("OPENAI_API_KEY not set")

    response = openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a financial sentiment classifier."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
