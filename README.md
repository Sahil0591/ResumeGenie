# ResumeGenie: Compliance-First Autonomous Recruitment Agent

Global API-driven job ingestion + intelligent filtering + Watson/Granite résumé generation.

## Architecture Overview
Agents (Python modules) implement discrete capabilities and can be mapped to IBM watsonx Orchestrate "Skills" for workflow automation:

| Capability | Python Module | Orchestrate Skill Concept | Notes |
|------------|---------------|---------------------------|-------|
| Ingestion (Adzuna/RemoteOK/WWR/etc.) | `agents/ingestion.py` | Fetch Jobs | Official APIs / RSS only (no scraping) |
| Analysis (skills, timezone, seniority) | `agents/analysis.py` | Analyze Job | Regex / NLP placeholder; extend with Granite model |
| GitHub Profile Enrichment | `agents/github_scanner.py` | Fetch GitHub Projects | GraphQL/API integration optional |
| Ghost Job Validation | `agents/ghost_validator.py` | Validate Apply URL | HEAD request prevents dead listings |
| Resume + Cheat Sheet Generation | `agents/resume_writer.py` / `agents/cheat_sheet.py` | Generate Application Package | Granite 3.0 for ATS-aligned rewriting |
| Orchestration Script | `scripts/run_pipeline.py` | Composite Flow | Sequence of skills or single orchestrated run |

## Standard Job Object (In-Memory)
```
{
  id, source, title, company, description, location, salary,
  apply_url, hash, fetched_at, skills_extracted, timezones,
  seniority, remote_flag, score
}
```

## Watson Orchestrate Integration
1. Each Python function becomes a **Skill** (deploy as containerized microservice or serverless endpoint).  
2. A Flow in Orchestrate sequences: FetchJobs → AnalyzeJob → FilterJobs → ValidateJob → EnrichProfile → GenerateResume.  
3. Inputs (e.g. user skills, GitHub username) passed as flow context variables; outputs appended to the flow state.  
4. Granite model calls (future) encapsulated in a `GenerateResume` skill using IBM Watson Machine Learning / foundation model endpoint.  
5. Event logging (future) can push status updates (INGESTED, VALIDATED, PACKAGE_BUILT) to watsonx.data or PostgreSQL for audit/compliance.  
6. Error handling: retries (& timeouts) wrapped with `tenacity` in each skill; Orchestrate catches failures and can branch (e.g., skip invalid jobs).  

## Running Locally
```cmd
py -3.10 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python scripts/run_pipeline.py
```

## Environment Variables (example .env)
```
ADZUNA_ID=xxxxx
ADZUNA_KEY=xxxxx
GITHUB_TOKEN=optional_for_private_or_higher_rate
IBM_WATSONX_API_KEY=xxxxx
IBM_WATSONX_PROJECT_ID=xxxxx
```

## Next Steps
- Add USAJobs & HN Algolia connectors.
- Persist jobs to PostgreSQL (SQLAlchemy models).
- Add Granite semantic scoring for skill relevance.
- Implement CI workflow, security scans.
- Containerize for Orchestrate deployment.

## Granite Model Usage

The file `agents/granite_client.py` wraps watsonx foundation model calls. Resume generation in `scripts/run_pipeline.py` uses `build_granite_resume()` which:

1. Builds a prompt with job description, candidate skills, and relevant projects.
2. Calls the Granite model (default `granite-3-8b-instruct`).
3. Falls back to local formatting if credentials are missing or the request fails.

Environment variables required (see `.env.example`):
`IBM_WATSONX_API_KEY`, `IBM_WATSONX_PROJECT_ID`, `IBM_REGION`, `GRANITE_MODEL_ID`.

To change model or parameters, edit `MODEL_ID` and decoding settings inside `granite_client.py`.

## Testing (placeholder)
```cmd
pytest -q
```

## License
Choose MIT / Apache-2.0 as needed.
