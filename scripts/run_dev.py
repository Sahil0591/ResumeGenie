import os
import sys
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

# Load optional local env files
# Prioritize .env.dev if present, then .env
if os.path.exists(".env.dev"):
    load_dotenv(".env.dev")
else:
    load_dotenv()


def main():
    # Ensure imports resolve when running from scripts/ on Windows
    root = Path(__file__).resolve().parents[1]
    try:
        # Change working directory to repo root so api_server.py is importable
        os.chdir(root)
    except Exception:
        pass
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    # Force dev settings for local Ollama (override any existing values)
    os.environ["LLM_PROVIDER"] = "ollama"
    os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
    os.environ["OLLAMA_MODEL"] = "llama3:latest"
    os.environ.setdefault("CORS_ALLOW_ORIGINS", "http://localhost:3000")

    # Ensure cloud keys aren’t used in dev
    os.environ.setdefault("GEMINI_API_KEY", "")

    # Port can be overridden via PORT env or first CLI arg
    port = int(os.getenv("PORT", "8000"))
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass

    print("\n[DEV] Starting ResumeGenie API (Ollama mode)")
    print(
        f"[DEV] LLM_PROVIDER={os.getenv('LLM_PROVIDER')}  "
        f"OLLAMA_BASE_URL={os.getenv('OLLAMA_BASE_URL')}  "
        f"OLLAMA_MODEL={os.getenv('OLLAMA_MODEL')}"
    )
    print(f"[DEV] CORS_ALLOW_ORIGINS={os.getenv('CORS_ALLOW_ORIGINS')}  PORT={port}\n")

    # Run FastAPI; disable reload on Windows to avoid multiprocessing spawn errors
    is_windows = os.name == "nt"
    if is_windows:
        print("[DEV] Windows detected: running without --reload to avoid spawn errors.")
    uvicorn.run("api_server:app", host="0.0.0.0", port=port, reload=not is_windows)


if __name__ == "__main__":
    # Windows multiprocessing guard for uvicorn reload
    try:
        import multiprocessing as mp
        mp.freeze_support()
    except Exception:
        pass
    main()
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
