## ...existing code...

# --- Cloudflare Access header helper ---
import os
import time
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv
load_dotenv()

def get_llm_provider() -> str:
    return os.getenv("LLM_PROVIDER", "gemini").lower()

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

def get_gemini_key() -> Optional[str]:
    return os.getenv("GEMINI_API_KEY")

def get_gemini_model() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")

def _gemini_headers() -> Dict[str, str]:
    return {"Content-Type": "application/json"}

def get_gemini_timeout() -> int:
    try:
        return int(os.getenv("GEMINI_TIMEOUT", "60"))
    except Exception:
        return 60

def gemini_generate(prompt: str, options: Optional[Dict[str, Any]] = None, timeout: Optional[int] = None) -> Optional[str]:
    key = get_gemini_key()
    if not key:
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{get_gemini_model()}:generateContent?key={key}"
    payload: Dict[str, Any] = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}]
    }
    if options:
        payload["generationConfig"] = options
    t = timeout or get_gemini_timeout()
    for attempt in range(3):
        try:
            resp = requests.post(url, json=payload, headers=_gemini_headers(), timeout=t)
            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                text = "".join(p.get("text", "") for p in parts).strip()
                return text or None
            return None
        except requests.exceptions.Timeout:
            if attempt < 2:
                time.sleep(1 + attempt)
                continue
            print("[ERROR] Gemini request timed out after retries")
            return None
        except Exception as e:
            print(f"[ERROR] Gemini request failed: {e}")
            return None

def gemini_health() -> Dict[str, Any]:
    key = get_gemini_key()
    model = get_gemini_model()
    if not key:
        return {"status_code": 400, "error": "Missing GEMINI_API_KEY", "body": ""}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    payload = {"contents": [{"role": "user", "parts": [{"text": "ping"}]}]}
    try:
        resp = requests.post(url, json=payload, headers=_gemini_headers(), timeout=10)
        return {
            "status_code": resp.status_code,
            "error": None if resp.ok else "Gemini error",
            "body": resp.text[:200],
        }
    except Exception as e:
        return {"status_code": 0, "error": str(e), "body": ""}

def safe_generate(prompt: str) -> Optional[str]:
    if get_llm_provider() == "gemini":
        return gemini_generate(prompt, options={"temperature": 0})
    # Fallback to local Ollama
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
