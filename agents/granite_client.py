import os
import requests
from typing import Optional

API_KEY = os.getenv("IBM_WATSONX_API_KEY")
PROJECT_ID = os.getenv("IBM_WATSONX_PROJECT_ID")  # project or space id
REGION = os.getenv("IBM_REGION", "us-south")
MODEL_ID = os.getenv("GRANITE_MODEL_ID", "granite-3-8b-instruct")
BASE_URL = f"https://{REGION}.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
TIMEOUT = int(os.getenv("GRANITE_TIMEOUT", "45"))


def generate(prompt: str, max_tokens: int = 600, temperature: float = 0.2) -> str:
    if not API_KEY or not PROJECT_ID:
        raise RuntimeError("Missing IBM Watsonx credentials (API_KEY / PROJECT_ID)")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
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
    r = requests.post(BASE_URL, json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    return data["results"][0]["generated_text"]


def safe_generate(prompt: str) -> Optional[str]:
    try:
        return generate(prompt)
    except Exception:
        return None

if __name__ == "__main__":
    test = safe_generate("Summarize: Python developer optimizing cloud costs.")
    print(test)
