## ...existing code...

# --- Cloudflare Access header helper ---
import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv
load_dotenv()

def get_ollama_base_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def get_ollama_model() -> str:
    return os.getenv("OLLAMA_MODEL", "llama3:latest")

def get_ollama_timeout() -> int:
    return int(os.getenv("OLLAMA_TIMEOUT", "45"))

def get_ollama_headers() -> dict:
    headers = {"User-Agent": "ResumeGenie/Cloudflare"}
    cf_id = os.getenv("CF_ACCESS_CLIENT_ID")
    cf_secret = os.getenv("CF_ACCESS_CLIENT_SECRET")
    if cf_id and cf_secret:
        headers["CF-Access-Client-Id"] = cf_id
        headers["CF-Access-Client-Secret"] = cf_secret
    return headers

def generate_text(prompt: str, model: Optional[str] = None, stream: bool = False, options: Optional[Dict[str, Any]] = None) -> Optional[str]:
    base = get_ollama_base_url().rstrip('/')
    url = f"{base}/api/generate"
    payload = {
        "model": model or get_ollama_model(),
        "prompt": prompt,
        "stream": stream,
    }
    if options:
        payload["options"] = options
    headers = get_ollama_headers()
    headers["Content-Type"] = "application/json"
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=get_ollama_timeout())
        r.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Ollama request failed: {e}")
        return None
    try:
        data = r.json()
        return data.get("response")
    except Exception as e:
        print(f"[ERROR] Ollama JSON parse failed: {e}")
        return None

def safe_generate(prompt: str) -> Optional[str]:
    fallbacks = [get_ollama_model(), "mistral:7b", "llama3.1:8b", "phi3:mini"]
    for m in fallbacks:
        result = generate_text(prompt, model=m, stream=False)
        if result:
            return result
    return None

# --- Diagnostic GET for /api/tags ---
def ollama_get_tags() -> dict:
    url = f"{get_ollama_base_url().rstrip('/')}/api/tags"
    headers = get_ollama_headers()
    try:
        r = requests.get(url, headers=headers, timeout=get_ollama_timeout())
        return {
            "status_code": r.status_code,
            "body": r.text[:200],
            "error": None
        }
    except Exception as e:
        return {
            "status_code": None,
            "body": "",
            "error": str(e)
        }
