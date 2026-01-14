# ResumeGenie: Backend + Frontend (Gemini + FastAPI + Next.js)

Global API-driven job ingestion + intelligent filtering + cloud-hosted LLM résumé generation via Google Gemini.

## Architecture Overview
Agents (Python modules) implement discrete capabilities for a lightweight, local workflow:

| Capability | Python Module | Notes |
|------------|---------------|-------|
| Ingestion (Adzuna/RemoteOK/WWR/etc.) | `agents/ingestion.py` | Official APIs / RSS only (no scraping) |
| Analysis (skills, timezone, seniority) | `agents/analysis.py` | Regex / heuristic scoring |
| GitHub Profile Enrichment | `agents/github_scanner.py` | GraphQL/API integration optional |
| Ghost Job Validation | `agents/ghost_validator.py` | HEAD request prevents dead listings |
| Resume + Cheat Sheet Generation | `agents/resume_writer.py` / `agents/cheat_sheet.py` | Gemini via Generative Language API |
| Orchestration Script | `agents/agent_runner.py` | Ranks top 5 and calls /generate |

## Standard Job Object (DB)
```
{
  id, source, title, company, description, location, salary,
  apply_url, seniority, remote_flag, fetched_at, score
}
```

## Running Locally
```cmd
py -3.10 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python api_server.py
```

Frontend (Next.js) runs separately; set the API base URL:
```cmd
# PowerShell
$env:NEXT_PUBLIC_API_BASE="http://localhost:8000"
# or in .env.local
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

## Environment Variables
Backend `.env` (see `.env.example`, do NOT commit secrets):
```
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash-latest
CORS_ALLOW_ORIGINS=http://localhost:3000,https://your-app.vercel.app
```

Frontend `.env.local`:
```
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

Optional (data sources):
```
ADZUNA_ID=xxxxx
ADZUNA_KEY=xxxxx
GITHUB_TOKEN=optional_for_private_or_higher_rate
```

## LLM Usage
`agents/llm_client.py` supports Google Gemini and (optionally) local Ollama for dev. `safe_generate()` routes to Gemini when `LLM_PROVIDER=gemini` and falls back to Ollama otherwise.

Gemini endpoint used:
```
POST https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}
```

## Endpoints
- GET /jobs: list ranked jobs
- POST /ingest: start ingestion in background
- GET /export_jobs: export all jobs as JSON
- GET /profile: read profile JSON from master_profile.json
- POST /profile: write profile JSON
- POST /generate/{id}: build tailored resume + cheat sheet; writes resume_{sanitized_id}.pdf
- PATCH /jobs/{id}: update selected job fields
- Static mount: /static serves generated PDFs and assets
 - GET /health: basic service up check
 - GET /health/config: echo environment as seen by the server
 - GET /health/llm: provider-aware health (Gemini/Ollama)
 - GET /health/llm-generate: test a tiny generation and return a preview

## Agent Runner
Run the lightweight agent to generate top 5 automatically:
```cmd
python -m agents.agent_runner
```

## Deployment
Backend (Render):
- Set env vars: `LLM_PROVIDER`, `GEMINI_API_KEY`, `GEMINI_MODEL`, `CORS_ALLOW_ORIGINS`
- Start command: `uvicorn api_server:app --host 0.0.0.0 --port 8000`
- Verify: `/health/config` and `/health/llm` should be OK

Frontend (Vercel):
- Root directory: `frontend/`
- Env var: `NEXT_PUBLIC_API_BASE=https://<your-render-service>.onrender.com`
- Deploy and confirm the app can call `/health/llm`

## Next Steps
- Add connectors (USAJobs, HN Algolia)
- Improve heuristic scoring and ranking
- Implement CI workflow, security scans
- Optional: containerize for deployment
