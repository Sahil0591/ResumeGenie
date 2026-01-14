import os
import sys
import uvicorn
from dotenv import load_dotenv

# Load optional local env files
# Prioritize .env.dev if present, then .env
if os.path.exists(".env.dev"):
    load_dotenv(".env.dev")
else:
    load_dotenv()

# Force dev settings for local Ollama
os.environ.setdefault("LLM_PROVIDER", "ollama")
os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434")
os.environ.setdefault("OLLAMA_MODEL", "llama3:latest")
os.environ.setdefault("CORS_ALLOW_ORIGINS", "http://localhost:3000")

# Port can be overridden via PORT env or first CLI arg
port = int(os.getenv("PORT", "8000"))
if len(sys.argv) > 1:
    try:
        port = int(sys.argv[1])
    except ValueError:
        pass

print("\n[DEV] Starting ResumeGenie API (Ollama mode)")
print(f"[DEV] LLM_PROVIDER={os.getenv('LLM_PROVIDER')}  OLLAMA_BASE_URL={os.getenv('OLLAMA_BASE_URL')}  OLLAMA_MODEL={os.getenv('OLLAMA_MODEL')}")
print(f"[DEV] CORS_ALLOW_ORIGINS={os.getenv('CORS_ALLOW_ORIGINS')}  PORT={port}\n")

# Run FastAPI with reload for local development
uvicorn.run("api_server:app", host="0.0.0.0", port=port, reload=True)
