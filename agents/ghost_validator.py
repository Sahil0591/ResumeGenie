import requests
from typing import Dict


def validate_job(job: Dict) -> Dict:
    url = job.get("apply_url")
    alive = False
    status = None
    try:
        r = requests.head(url, allow_redirects=True, timeout=10)
        status = r.status_code
        alive = status and status < 400
    except Exception:
        status = 0
    job["ghost_status"] = status
    job["valid"] = alive
    return job
