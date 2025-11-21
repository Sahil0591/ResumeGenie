import json
from dotenv import load_dotenv
load_dotenv()
from agents.ingestion import ingest_all
from agents.analysis import analyze_job, filter_jobs, rank_jobs
from agents.github_scanner import fetch_repos, enrich_profile, filter_relevant_projects
from agents.ghost_validator import validate_job
from agents.resume_writer import build_granite_resume, build_cheat_sheet
from agents.cheat_sheet import save_cheat_sheet
from db.db import get_session
from db.persist import upsert_jobs, save_application

PROFILE_PATH = "master_profile.json"


def load_profile(path: str = PROFILE_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main(limit: int = 5):
    profile = load_profile()
    jobs = ingest_all()
    jobs = [analyze_job(j) for j in jobs]
    jobs = filter_jobs(jobs, {"skills": profile.get("skills", []), "remote_only": True})
    jobs = rank_jobs(jobs)
    # Persist enriched jobs (after ranking so score stored)
    with get_session() as s:
        inserted = upsert_jobs(s, jobs)
    print(f"Upserted {len(inserted)} new jobs into database")

    repos = fetch_repos(profile.get("github_username", ""))
    profile = enrich_profile(profile, repos)

    results = []
    for job in jobs[:limit]:
        job = validate_job(job)
        if not job.get("valid"):
            continue
        rel_projects = filter_relevant_projects(repos, job)
        resume_md = build_granite_resume(profile, job, rel_projects)
        cheat = build_cheat_sheet(profile, job)
        results.append({"job": job, "resume": resume_md, "cheat": cheat})
        # Persist application package
        try:
            with get_session() as s:
                pkg_id = save_application(s, job["id"], resume_md, cheat)
            print(f"Saved application package {pkg_id} for job {job['id']}")
        except Exception as e:
            print(f"Failed to save application for job {job['id']}: {e}")

    for r in results:
        jid = r["job"]["id"].replace("/", "_")
        resume_file = f"resume_{jid}.md"
        cheat_file = f"cheat_{jid}.json"
        with open(resume_file, "w", encoding="utf-8") as f:
            f.write(r["resume"])
        save_cheat_sheet(r["cheat"], cheat_file)
    print(f"Generated {len(results)} application packages")


if __name__ == "__main__":
    main()
