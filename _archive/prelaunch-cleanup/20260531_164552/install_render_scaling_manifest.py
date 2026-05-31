from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / "backups" / f"render_scaling_manifest_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

RENDER_YAML = """services:
  - type: web
    name: ecommerce-ai-agent-platform-api
    env: python
    plan: starter
    buildCommand: pip install -r requirements.txt
    startCommand: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --workers ${WEB_CONCURRENCY:-2}
    envVars:
      - key: WEB_CONCURRENCY
        value: "2"
      - key: OWNER_APPROVAL_REQUIRED
        value: "true"
      - key: LIVE_EXTERNAL_CALLS_ENABLED
        value: "false"

  - type: worker
    name: ecommerce-ai-agent-platform-worker
    env: python
    plan: starter
    buildCommand: pip install -r requirements.txt
    startCommand: python -m backend.app.runtime.background_worker_loop
    envVars:
      - key: WORKER_CONCURRENCY
        value: "2"
      - key: OWNER_APPROVAL_REQUIRED
        value: "true"
      - key: LIVE_EXTERNAL_CALLS_ENABLED
        value: "false"
"""

def backup(path: Path):
    if path.exists():
        BACKUP.mkdir(parents=True, exist_ok=True)
        (BACKUP / path.name).write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")

def main():
    path = ROOT / "render.yaml"
    backup(path)
    path.write_text(RENDER_YAML, encoding="utf-8")

    print("RENDER_SCALING_MANIFEST_INSTALLED")
    print("Backup folder:", BACKUP)
    print("Created/updated:", path)
    print("Safety:")
    print("- LIVE_EXTERNAL_CALLS_ENABLED remains false in manifest")
    print("- OWNER_APPROVAL_REQUIRED remains true")
    print("- Web worker count starts at 2")
    print("- Dedicated worker process declared but not manually activated by this script")

if __name__ == "__main__":
    main()