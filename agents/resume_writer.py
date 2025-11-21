from typing import Dict, List
from agents.granite_client import safe_generate


def _format_local_resume(master_profile: Dict, job: Dict, projects: List[Dict]) -> str:
    lines: List[str] = []
    lines.append(f"# Resume Target: {job.get('title')}")
    lines.append(f"Company: {job.get('company')}")
    lines.append("## Key Skills")
    lines.append(", ".join(sorted(set(master_profile.get("skills", [])))))
    if projects:
        lines.append("## Relevant Projects")
        for p in projects:
            desc = (p.get("description") or "")[:80]
            lines.append(f"- {p['name']}: {desc}")
    lines.append("## Experience (Action → Context → Result)")
    for exp in master_profile.get("experience", []):
        lines.append(f"- Action: {exp['action']}\n  Context: {exp['context']}\n  Result: {exp['result']}")
    return "\n".join(lines)


def build_granite_resume(master_profile: Dict, job: Dict, projects: List[Dict]) -> str:
    prompt = f"""
You are an ATS optimization assistant. Generate a tailored resume section.

JOB TITLE: {job.get('title')}
COMPANY: {job.get('company')}
JOB DESCRIPTION:
{job.get('description','')[:1500]}

CANDIDATE SKILLS: {', '.join(master_profile.get('skills', []))}
PROJECTS:
{'; '.join([p['name'] + ': ' + (p.get('description','')[:120]) for p in projects])}

Output Markdown with sections:
1. Summary (2 sentences)
2. Core Skills (comma separated)
3. Achievements (Action → Context → Result bullets) (3-5 items)
Use only real candidate skills.
"""
    generated = safe_generate(prompt)
    if generated:
        return generated
    return _format_local_resume(master_profile, job, projects)


def build_cheat_sheet(master_profile: Dict, job: Dict) -> Dict:
    return {
        "job_id": job.get("id"),
        "years_experience": master_profile.get("years_experience"),
        "primary_stack": ", ".join(master_profile.get("skills", [])[:5]),
        "work_auth": master_profile.get("work_auth"),
        "salary_expectation": master_profile.get("salary_expectation", "Negotiable"),
    }
