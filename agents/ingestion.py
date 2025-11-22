import os
import time
import hashlib
import requests
import feedparser
from typing import Dict, List

# NOTE: Replace environment variables with secrets management / watsonx Orchestrate inputs.
ADZUNA_APP_ID = os.getenv("ADZUNA_ID", "")
ADZUNA_APP_KEY = os.getenv("ADZUNA_KEY", "")
USAJOBS_API_KEY = os.getenv("USAJOBS_API_KEY", "")  # developer key
USAJOBS_USER_AGENT = os.getenv("USAJOBS_USER_AGENT", "")  # descriptive UA with contact email


def _hash_job(title: str, company: str, location: str, desc: str) -> str:
    return hashlib.sha256((title + company + location + desc[:200]).encode()).hexdigest()


def normalize_job(raw: Dict, source: str) -> Dict:
    desc = raw.get("description", "")
    return {
        "id": f"{source}_{raw.get('id')}",
        "source": source,
        "title": raw.get("title"),
        "company": raw.get("company"),
        "description": desc,
        "location": raw.get("location"),
        "salary": raw.get("salary"),
        "apply_url": raw.get("apply_url"),
        "hash": _hash_job(raw.get("title", ""), raw.get("company", ""), raw.get("location", ""), desc),
        "fetched_at": int(time.time()),
        "skills_extracted": [],  # populated later
    }


def fetch_adzuna(country: str = "gb", page: int = 1, what: str = "python") -> List[Dict]:
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        return []
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": 50,
        "content-type": "application/json",
        "what": what,
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
    except Exception:
        return []
    jobs: List[Dict] = []
    for j in r.json().get("results", []):
        jobs.append(
            normalize_job(
                {
                    "id": str(j.get("id")),
                    "title": j.get("title"),
                    "company": j.get("company", {}).get("display_name", ""),
                    "description": j.get("description", ""),
                    "location": j.get("location", {}).get("display_name", ""),
                    "salary": j.get("salary_min") or j.get('salary_is_predicted'), 
                    "apply_url": j.get("redirect_url", ""),
                },
                source="adzuna",
            )
        )
    return jobs


def fetch_remoteok() -> List[Dict]:
    try:
        r = requests.get("https://remoteok.com/api", timeout=15)
        if r.status_code != 200:
            return []
        data = r.json()[1:]  # first element is metadata
    except Exception:
        return []
    out: List[Dict] = []
    for item in data:
        out.append(
            normalize_job(
                {
                    "id": str(item.get("id")),
                    "title": item.get("position"),
                    "company": item.get("company"),
                    "description": item.get("description", ""),
                    "location": item.get("location", "Remote"),
                    "salary": item.get("salary", ""),
                    "apply_url": item.get("url", ""),
                },
                source="remoteok",
            )
        )
    return out


def fetch_wwr_rss() -> List[Dict]:
    feed = feedparser.parse("https://weworkremotely.com/remote-jobs.rss")
    out: List[Dict] = []
    for e in feed.entries:
        out.append(
            normalize_job(
                {
                    "id": e.get("id", e.link),
                    "title": e.title,
                    "company": e.get("author", ""),
                    "description": e.get("summary", ""),
                    "location": "Remote",
                    "salary": "",
                    "apply_url": e.link,
                },
                source="wwr",
            )
        )
    return out


def fetch_usajobs(page: int = 1, keyword: str = "python") -> List[Dict]:
    # Requires both API key and user agent per USAJOBS API docs
    if not USAJOBS_API_KEY or not USAJOBS_USER_AGENT:
        return []
    url = "https://data.usajobs.gov/api/search"
    headers = {
        "User-Agent": USAJOBS_USER_AGENT,
        "Accept": "application/json",
        "Authorization-Key": USAJOBS_API_KEY,
    }
    params = {"Page": page, "ResultsPerPage": 25, "Keyword": keyword}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=20)
        if r.status_code != 200:
            return []
        data = r.json().get("SearchResult", {}).get("SearchResultItems", [])
    except Exception:
        return []
    out: List[Dict] = []
    for item in data:
        pos = item.get("MatchedObjectDescriptor", {})
        out.append(
            normalize_job(
                {
                    "id": pos.get("PositionID"),
                    "title": pos.get("PositionTitle"),
                    "company": pos.get("OrganizationName"),
                    "description": pos.get("UserArea", {}).get("Details", {}).get("JobSummary", ""),
                    "location": ", ".join([l.get("LocationName") for l in pos.get("PositionLocation", [])]) if pos.get("PositionLocation") else "",
                    "salary": pos.get("PositionRemuneration", [{}])[0].get("MinimumRange"),
                    "apply_url": (pos.get("ApplyURI", [""]) or [""])[0],
                },
                source="usajobs",
            )
        )
    return out


def fetch_hn_jobs(query: str = "python", page: int = 0) -> List[Dict]:
    url = "https://hn.algolia.com/api/v1/search"
    params = {"query": query, "tags": "job", "page": page}
    try:
        r = requests.get(url, params=params, timeout=15)
        if r.status_code != 200:
            return []
        hits = r.json().get("hits", [])
    except Exception:
        return []
    out: List[Dict] = []
    for h in hits:
        out.append(
            normalize_job(
                {
                    "id": h.get("objectID"),
                    "title": h.get("title"),
                    "company": h.get("author", ""),
                    "description": h.get("story_text") or h.get("title", ""),
                    "location": "Remote",
                    "salary": "",
                    "apply_url": h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}",
                },
                source="hn",
            )
        )
    return out


# TODO: Implement USAJobs and HN Algolia connectors.

def ingest_all(countries: List[str] = None) -> List[Dict]:
    if countries is None:
        countries = ["gb", "in", "ae", "us"]
    jobs: List[Dict] = []
    # Adzuna multi-country
    if ADZUNA_APP_ID and ADZUNA_APP_KEY:
        for c in countries:
            jobs += fetch_adzuna(country=c, page=1, what="python")
    # Remote sources
    jobs += fetch_remoteok()
    jobs += fetch_wwr_rss()
    # USAJobs (requires email + user agent)
    jobs += fetch_usajobs(page=1, keyword="python")
    # Hacker News job postings
    jobs += fetch_hn_jobs(query="python", page=0)
    return dedupe(jobs)


def dedupe(jobs: List[Dict]) -> List[Dict]:
    seen = set()
    out: List[Dict] = []
    for j in jobs:
        h = j.get("hash")
        if h not in seen:
            seen.add(h)
            out.append(j)
    return out


if __name__ == "__main__":
    collected = ingest_all()
    print(f"Ingested {len(collected)} jobs")
