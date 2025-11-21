import requests
from typing import Dict, List

GITHUB_API = "https://api.github.com"


def fetch_repos(username: str) -> List[Dict]:
    url = f"{GITHUB_API}/users/{username}/repos"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    repos = []
    for repo in r.json():
        repos.append(
            {
                "name": repo["name"],
                "description": repo.get("description", ""),
                "language": repo.get("language"),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "topics": repo.get("topics", []),
                "url": repo.get("html_url"),
            }
        )
    return repos


def enrich_profile(master_profile: Dict, repos: List[Dict]) -> Dict:
    master_profile["projects"] = repos
    return master_profile


def filter_relevant_projects(repos: List[Dict], job: Dict) -> List[Dict]:
    title_desc = (job.get("title", "") + " " + job.get("description", "")).lower()
    relevant = [r for r in repos if r.get("language") and r["language"].lower() in title_desc]
    return relevant[:5]
