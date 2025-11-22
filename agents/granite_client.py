import os
import requests
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("IBM_WATSONX_API_KEY")
PROJECT_ID = os.getenv("IBM_WATSONX_PROJECT_ID", "ea8f1e60-8b49-4ad1-985e-f99abb3b04d0")
MODEL_ID = os.getenv("GRANITE_MODEL_ID", "ibm/granite-3-8b-instruct")
TIMEOUT = int(os.getenv("GRANITE_TIMEOUT", "45"))

# Cache the token
_cached_token = None


def get_iam_token() -> str:
    """Get IBM Cloud IAM access token"""
    global _cached_token
    
    if not API_KEY:
        raise RuntimeError("Missing IBM_WATSONX_API_KEY")
    
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": API_KEY
    }
    
    response = requests.post(url, headers=headers, data=data, timeout=10)
    response.raise_for_status()
    _cached_token = response.json()["access_token"]
    return _cached_token


def generate(prompt: str, max_tokens: int = 600, temperature: float = 0.2) -> str:
    if not API_KEY or not PROJECT_ID:
        raise RuntimeError("Missing IBM Watsonx credentials (API_KEY / PROJECT_ID)")
    
    # Get IAM token
    token = get_iam_token()
    
    # Use Watson ML endpoint from your screenshot
    base_url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "stop_sequences": [],
        },
        "model_id": MODEL_ID,
        "project_id": PROJECT_ID,
    }
    
    r = requests.post(base_url, headers=headers, json=payload, timeout=TIMEOUT)
    
    # Print detailed error if request fails
    if r.status_code != 200:
        print(f"[ERROR] Status Code: {r.status_code}")
        print(f"[ERROR] Response: {r.text}")
    
    r.raise_for_status()
    data = r.json()
    return data["results"][0]["generated_text"]


def generate_with_model(prompt: str, model_id: str, max_tokens: int = 600, temperature: float = 0.2) -> str:
    """Generate text with a specific model ID"""
    if not API_KEY or not PROJECT_ID:
        raise RuntimeError("Missing IBM Watsonx credentials (API_KEY / PROJECT_ID)")
    
    token = get_iam_token()
    base_url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "stop_sequences": [],
        },
        "model_id": model_id,
        "project_id": PROJECT_ID,
    }
    
    r = requests.post(base_url, headers=headers, json=payload, timeout=TIMEOUT)
    
    if r.status_code != 200:
        print(f"[ERROR] Status Code: {r.status_code}")
        print(f"[ERROR] Response: {r.text}")
    
    r.raise_for_status()
    data = r.json()
    return data["results"][0]["generated_text"]


def safe_generate(prompt: str) -> Optional[str]:
    # Try multiple Granite model IDs
    alternative_models = [
        "ibm/granite-3-8b-instruct",
        "ibm/granite-13b-instruct-v2",
        "ibm/granite-13b-chat-v2",
        "ibm/granite-20b-multilingual",
        "meta-llama/llama-3-70b-instruct",
    ]
    
    for model_id in alternative_models:
        try:
            print(f"[INFO] Trying model: {model_id}")
            result = generate_with_model(prompt, model_id)
            print(f"[SUCCESS] Model {model_id} worked!")
            return result
        except Exception as e:
            print(f"[WARN] Model {model_id} failed: {type(e).__name__}")
            continue
    
    print(f"[ERROR] All models failed. Check available models in your watsonx.ai project.")
    return None

if __name__ == "__main__":
    test = safe_generate("Summarize: Python developer optimizing cloud costs.")
    print(test)
