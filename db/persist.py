from typing import List, Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Job, ApplicationPackage


def upsert_jobs(session: Session, jobs: List[Dict[str, Any]]) -> List[str]:
    """Insert new jobs by primary key id; skip existing ids.
    Returns list of inserted job ids."""
    if not jobs:
        return []
    ids = [j.get("id") for j in jobs if j.get("id")]
    existing_ids = set()
    if ids:
        stmt = select(Job.id).where(Job.id.in_(ids))
        for row in session.execute(stmt):
            existing_ids.add(row[0])
    inserted: List[str] = []
    for j in jobs:
        jid = j.get("id")
        if not jid or jid in existing_ids:
            continue
        obj = Job(
            id=jid,
            source=j.get("source", ""),
            title=j.get("title", ""),
            company=j.get("company"),
            description=j.get("description", ""),
            location=j.get("location"),
            salary=str(j.get("salary", "")) if j.get("salary") is not None else None,
            apply_url=j.get("apply_url"),
            seniority=j.get("seniority"),
            remote_flag=j.get("remote_flag", False),
            score=j.get("score"),
        )
        session.add(obj)
        inserted.append(jid)
    session.commit()
    return inserted


def save_application(session: Session, job_id: str, resume_markdown: str, cheat_sheet: Dict[str, Any], user_email: str, relevance_score: float | int | None) -> str:
    """Persist an application package embedding user context.
    Skips creation if a package already exists for the same job + user_email.
    Returns new package id or existing package id if skipped."""
    if not job_id:
        raise ValueError("job_id is required")
    stmt = select(Job).where(Job.id == job_id)
    job_obj = session.execute(stmt).scalar_one_or_none()
    if job_obj is None:
        raise ValueError("Job not found; insert job before saving application")
    # Duplicate check: any existing package with same job_id and user_email inside JSON
    existing_stmt = select(ApplicationPackage).where(ApplicationPackage.job_id == job_id)
    for existing in session.execute(existing_stmt).scalars():
        try:
            if existing.cheat_sheet_json.get("user_email") == user_email:
                # Update relevance if newly computed score is higher
                prev_score = existing.cheat_sheet_json.get("relevance_score")
                if relevance_score is not None and (prev_score is None or relevance_score > prev_score):
                    existing.cheat_sheet_json["relevance_score"] = relevance_score
                    session.commit()
                return existing.id
        except Exception:
            pass
    # Embed user metadata in cheat sheet JSON
    if user_email:
        cheat_sheet["user_email"] = user_email
    if relevance_score is not None:
        cheat_sheet["relevance_score"] = relevance_score
    pkg = ApplicationPackage(
        job_id=job_id,
        resume_markdown=resume_markdown,
        cheat_sheet_json=cheat_sheet,
    )
    session.add(pkg)
    session.commit()
    return pkg.id
