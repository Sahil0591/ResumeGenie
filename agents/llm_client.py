import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env at project root
load_dotenv()

# Minimal Ollama HTTP client
# Uses `OLLAMA_BASE_URL` (default http://localhost:11434) and `OLLAMA_MODEL`
# to generate text via /api/generate. Falls back to a reasonable default model.

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "45"))


def generate_text(prompt: str, model: Optional[str] = None, stream: bool = False, options: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Call Ollama `/api/generate` and return the generated text.
    - prompt: the input prompt
    - model: model name; defaults to `DEFAULT_MODEL`
    - stream: if True, Ollama streams responses; here we request non-streamed unless True
    - options: optional dict for model parameters (temperature, num_ctx, etc.)
    Returns the concatenated `response` field, or None on error.
    """
    base = OLLAMA_BASE_URL.rstrip('/')
    url = f"{base}/api/generate"
    payload = {
        "model": model or DEFAULT_MODEL,
        "prompt": prompt,
        "stream": stream,
    }
    if options:
        payload["options"] = options

    try:
        r = requests.post(url, json=payload, timeout=TIMEOUT)
        r.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Ollama request failed: {e}")
        return None

    # Non-stream response: a single JSON with `response`
    try:
        data = r.json()
        return data.get("response")
    except Exception as e:
        print(f"[ERROR] Ollama JSON parse failed: {e}")
        return None


def safe_generate(prompt: str) -> Optional[str]:
    """
    A simple wrapper that tries the default model and falls back to a few small models
    typically available locally. This prevents hard failures if a model is missing.
    """
    fallbacks = [DEFAULT_MODEL, "mistral:7b", "llama3.1:8b", "phi3:mini"]
    for m in fallbacks:
        result = generate_text(prompt, model=m, stream=False)
        if result:
            return result
    return None
