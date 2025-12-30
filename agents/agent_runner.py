"""
Lightweight agent runner:
- Fetches jobs from API
- Ranks top 5 by score (desc)
- Triggers resume generation for each via /generate/{id}

Usage:
  set NEXT_PUBLIC_API_BASE or API_BASE (optional)
  python -m agents.agent_runner
"""
import os
import requests

API_BASE = os.getenv("API_BASE") or os.getenv("NEXT_PUBLIC_API_BASE") or "http://localhost:8000"


def get_jobs(limit: int = 50):
    url = f"{API_BASE.rstrip('/')}/jobs?limit={limit}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


def generate(job_id: str):
    url = f"{API_BASE.rstrip('/')}/generate/{requests.utils.quote(job_id, safe='')}"
    r = requests.post(url, timeout=120)
    if r.status_code == 200:
        print(f"[OK] Generated for {job_id}: {r.json().get('pdf_url')}")
    else:
        print(f"[ERR] Failed for {job_id}: {r.text}")


def main():
    jobs = get_jobs(limit=100)
    # Sort by score desc if present
    def score_of(j):
        try:
            return int(j.get('score') or 0)
        except Exception:
            return 0
    ranked = sorted(jobs, key=score_of, reverse=True)
    top5 = ranked[:5]
    print(f"Found {len(jobs)} jobs. Generating for top {len(top5)}...")
    for j in top5:
        generate(j['id'])


if __name__ == "__main__":
    main()
