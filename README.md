# ResumeGenie: Simple Agentic Setup (Ollama + FastAPI)

Global API-driven job ingestion + intelligent filtering + local LLM résumé generation via Ollama.

## Architecture Overview
Agents (Python modules) implement discrete capabilities for a lightweight, local workflow:

| Capability | Python Module | Notes |
|------------|---------------|-------|
| Ingestion (Adzuna/RemoteOK/WWR/etc.) | `agents/ingestion.py` | Official APIs / RSS only (no scraping) |
| Analysis (skills, timezone, seniority) | `agents/analysis.py` | Regex / heuristic scoring |
| GitHub Profile Enrichment | `agents/github_scanner.py` | GraphQL/API integration optional |
| Ghost Job Validation | `agents/ghost_validator.py` | HEAD request prevents dead listings |
| Resume + Cheat Sheet Generation | `agents/resume_writer.py` / `agents/cheat_sheet.py` | Ollama local LLM (no Granite) |
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

## Environment Variables (example .env)
```
# Frontend ↔ Backend
NEXT_PUBLIC_API_BASE=http://localhost:8000

# Ollama client
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
```

Optional (data sources):
```
ADZUNA_ID=xxxxx
ADZUNA_KEY=xxxxx
GITHUB_TOKEN=optional_for_private_or_higher_rate
```

## Ollama Model Usage
The file `agents/llm_client.py` wraps the local Ollama HTTP API (`/api/generate`). Resume generation in `agents/resume_writer.py` calls `safe_generate()` which tries the configured model and small fallbacks.

To change model or parameters, set `OLLAMA_MODEL` or pass `options` in `generate_text()`.

Expose the backend to the internet via ngrok when needed:
```cmd
ngrok http 8000
# Then set NEXT_PUBLIC_API_BASE to the ngrok URL
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

## Agent Runner
Run the lightweight agent to generate top 5 automatically:
```cmd
python -m agents.agent_runner
```

## Next Steps
- Add connectors (USAJobs, HN Algolia)
- Improve heuristic scoring and ranking
- Implement CI workflow, security scans
- Optional: containerize for deployment
