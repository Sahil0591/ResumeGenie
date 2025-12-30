

import json
import os
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from agents.llm_client import safe_generate, OLLAMA_BASE_URL
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn

# Import your existing logic
from db.db import get_session
from db.models import Job, ApplicationPackage
from agents.ingestion import ingest_all
from agents.analysis import analyze_job, filter_jobs, rank_jobs
from agents.resume_writer import build_granite_resume, build_cheat_sheet
from agents.ghost_validator import validate_job
from db.persist import upsert_jobs, save_application


app = FastAPI(title="ResumeGenie API")

# --- Export Jobs Endpoint ---
@app.get("/export_jobs")
def export_jobs(db: Session = Depends(get_session)):
    jobs = db.query(Job).all()
    jobs_json = [
        {c.name: getattr(job, c.name) for c in job.__table__.columns}
        for job in jobs
    ]
    return jobs_json

# Profile file path
PROFILE_PATH = os.path.join(os.path.dirname(__file__), "master_profile.json")

# --- Profile Endpoints ---
@app.get("/profile")
def get_profile():
    if not os.path.exists(PROFILE_PATH):
        raise HTTPException(status_code=404, detail="Profile file not found")
    try:
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # If file is empty or not a dict, return empty profile
        if not isinstance(data, dict):
            return {}
        return data
    except json.JSONDecodeError:
        # If file is present but invalid JSON, return empty profile
        return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to read profile")

@app.post("/profile")
def save_profile(profile: dict):
    try:
        with open(PROFILE_PATH, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2)
        return {"status": "Profile saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to save profile")

# Serve static files (PDFs, etc.) from project root
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="."), name="static")

# Allow Next.js (port 3000) to talk to Python (port 8000)
# Configure CORS via env for safer deployments
cors_origins_env = os.getenv("CORS_ALLOW_ORIGINS", "*")
allow_origins = ["*"] if cors_origins_env.strip() == "*" else [o.strip() for o in cors_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Health Endpoint ---
@app.get("/health")
def health():
    return {"status": "ok"}

# Ollama connectivity check
@app.get("/health/llm")
def health_llm():
    try:
        sample = safe_generate("say ok")
        return {
            "ollama_base_url": OLLAMA_BASE_URL,
            "reachable": bool(sample),
            "sample": (sample or "")[:50],
        }
    except Exception:
        return {
            "ollama_base_url": OLLAMA_BASE_URL,
            "reachable": False,
            "sample": "",
        }

def run_ingestion_pipeline(db: Session):
    """Background task to fetch and process jobs"""
    print("Starting ingestion...")
    jobs = ingest_all()
    jobs = [analyze_job(j) for j in jobs]
    # Simple default filter
    jobs = filter_jobs(jobs, {"skills": ["Python", "AWS"], "remote_only": True})
    jobs = rank_jobs(jobs)
    upsert_jobs(db, jobs)
    print(f"Ingestion complete. Processed {len(jobs)} jobs.")

@app.get("/jobs")
def get_jobs(limit: int = 20, db: Session = Depends(get_session)):
    return db.query(Job).order_by(Job.score.desc()).limit(limit).all()

@app.post("/ingest")
def trigger_ingest(background_tasks: BackgroundTasks, db: Session = Depends(get_session)):
    """Trigger the ingestion pipeline in the background"""
    background_tasks.add_task(run_ingestion_pipeline, db)
    return {"status": "Ingestion started in background"}

@app.post("/generate/{job_id:path}")
def generate_application(job_id: str, db: Session = Depends(get_session)):
    """Generate resume and cheat sheet for a specific job"""
    job_record = db.query(Job).filter(Job.id == job_id).first()
    if not job_record:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Convert SQLAlchemy model to dict for your existing agents
    job_dict = {c.name: getattr(job_record, c.name) for c in job_record.__table__.columns}
    
    if os.path.exists(PROFILE_PATH):
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            profile = json.load(f)
    else:
        # Fallback only if file is missing
        profile = {
            "skills": ["Python", "AWS", "Terraform"], 
            "experience": [{"action": "Built API", "context": "FastAPI", "result": "Fast"}]
        }
    
    # Sanitize job_id for filename (match frontend logic)
    def sanitize_job_id(job_id):
        # Replace all non-alphanumeric characters with underscores
        return ''.join([c if c.isalnum() else '_' for c in job_id])
    sanitized_job_id = sanitize_job_id(job_id)

    # Run generation logic (Ollama-backed), using sanitized filename
    resume = build_granite_resume(profile, job_dict, profile.get("projects", []), sanitized_job_id)
    cheat = build_cheat_sheet(profile, job_dict)

    # Save to DB
    pkg_id = save_application(db, job_id, resume, cheat, "user@example.com", 0)

    # Preview uses generated text (LaTeX or fallback markdown)
    preview_md = resume if isinstance(resume, str) else str(resume)

    pdf_url = f"/static/resume_{sanitized_job_id}.pdf"
    
    return {
        "status": "Generated",
        "package_id": pkg_id,
        "preview_md": preview_md,
        "pdf_url": pdf_url
    }


@app.patch("/jobs/{job_id:path}")
def patch_job(job_id: str, update: dict, db: Session = Depends(get_session)):
    """PATCH a job with provided fields. Accepts a JSON body with fields to update."""
    job_record = db.query(Job).filter(Job.id == job_id).first()
    if not job_record:
        raise HTTPException(status_code=404, detail="Job not found")

    allowed_fields = {
        "title", "company", "location", "salary", "apply_url",
        "seniority", "remote_flag", "score", "description"
    }
    changed = False
    for k, v in update.items():
        if k in allowed_fields:
            setattr(job_record, k, v)
            changed = True
    if not changed:
        return {"status": "No changes"}
    try:
        db.commit()
        return {"status": "Updated", "id": job_id}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update job")


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()