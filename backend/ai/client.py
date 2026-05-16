"""
Shared Gemini client.

All AI modules import `client` and `fast_model` / `pro_model` from here.
FS1 will wire settings through config.py (PBI-02); until then we read
directly from the environment so the AI engineer can develop independently.
"""

import os

from dotenv import load_dotenv
from google import genai

load_dotenv()  # picks up backend/.env when running scripts directly

_api_key = os.environ.get("GOOGLE_API_KEY")
if not _api_key:
    raise EnvironmentError(
        "GOOGLE_API_KEY is not set. "
        "Copy backend/.env.example to backend/.env and fill it in."
    )

client = genai.Client(api_key=_api_key)

# Model names — override via env vars if needed
pro_model = os.environ.get("GEMINI_GENERATION_MODEL", "gemini-2.5-pro")
fast_model = os.environ.get("GEMINI_FAST_MODEL", "gemini-2.5-flash")
