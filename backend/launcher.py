from subprocess import Popen
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# backend через uvicorn (ВАЖНО: cwd = backend)
backend = Popen(
    [
        "uvicorn",
        "main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
    ],
    cwd=ROOT / "backend"
)

# frontend
frontend = Popen(
    "npm run dev",
    cwd=ROOT / "frontend",
    shell=True
)

try:
    backend.wait()
    frontend.wait()
except KeyboardInterrupt:
    backend.terminate()
    frontend.terminate()