import re
from typing import Dict, List

SKILL_PATTERN = re.compile(
    r"\b(python|aws|terraform|docker|kubernetes|react|node|sql|go|java|typescript)\b",
    re.IGNORECASE,
)
TZ_PATTERN = re.compile(r"(pst|est|cst|gmt|utc|india|uae|uk)", re.IGNORECASE)
SENIORITY_PATTERN = re.compile(r"\b(junior|mid|senior|lead|principal)\b", re.IGNORECASE)


def analyze_job(job: Dict) -> Dict:
    text = job.get("description", "")
    skills = list({m.group(0).lower() for m in SKILL_PATTERN.finditer(text)})
    tz = list({m.group(0).lower() for m in TZ_PATTERN.finditer(text)})
    seniority = SENIORITY_PATTERN.search(text)
    job["skills_extracted"] = skills
    job["timezones"] = tz
    job["seniority"] = seniority.group(0).lower() if seniority else None
    job["remote_flag"] = "remote" in text.lower()
    return job


def filter_jobs(jobs: List[Dict], user_pref: Dict) -> List[Dict]:
    out: List[Dict] = []
    required_skills = set(map(str.lower, user_pref.get("skills", [])))
    for j in jobs:
        if required_skills and not required_skills.intersection(set(j.get("skills_extracted", []))):
            continue
        if user_pref.get("remote_only") and not j.get("remote_flag"):
            continue
        out.append(j)
    return out


def rank_jobs(jobs: List[Dict]) -> List[Dict]:
    # Simple heuristic: skill count + remote flag bonus
    for j in jobs:
        j["score"] = len(j.get("skills_extracted", [])) + (2 if j.get("remote_flag") else 0)
    return sorted(jobs, key=lambda x: x.get("score", 0), reverse=True)
