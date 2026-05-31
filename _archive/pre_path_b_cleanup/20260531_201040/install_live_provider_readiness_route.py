from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / "backups" / f"live_provider_readiness_route_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
MAIN_FILE = ROOT / "backend" / "app" / "main.py"
TEST_FILE = ROOT / "test_live_provider_readiness_route.py"

ROUTE = r'''

@app.get("/admin/live-provider-readiness")
async def admin_live_provider_readiness():
    """
    Hosted provider readiness visibility.

    Safe:
    - No provider call
    - No spend
    - No external action
    - Does not expose secret values
    """
    import os

    openai_configured = bool(os.getenv("OPENAI_API_KEY"))
    live_external_calls_enabled = (os.getenv("LIVE_EXTERNAL_CALLS_ENABLED") or "false").lower() in {"1", "true", "yes", "on"}
    owner_approved_live_activation = (os.getenv("OWNER_APPROVED_LIVE_ACTIVATION") or "false").lower() in {"1", "true", "yes", "on"}
    owner_approval_required = (os.getenv("OWNER_APPROVAL_REQUIRED") or "true").lower() not in {"0", "false", "off"}

    return {
        "success": True,
        "check": "live_provider_readiness",
        "openai_configured": openai_configured,
        "live_external_calls_enabled": live_external_calls_enabled,
        "owner_approved_live_activation": owner_approved_live_activation,
        "owner_approval_required": owner_approval_required,
        "provider_execution_ready": bool(openai_configured and live_external_calls_enabled and owner_approved_live_activation),
        "worker_live_execution_enabled": (os.getenv("WORKER_LIVE_EXECUTION_ENABLED") or "false").lower() in {"1", "true", "yes", "on"},
        "secret_values_exposed": False,
        "provider_called": False,
        "spend_performed": False,
        "external_action_performed": False,
        "customer_safe": True,
        "status": "LIVE_PROVIDER_READY" if openai_configured and live_external_calls_enabled and owner_approved_live_activation else "LIVE_PROVIDER_NOT_READY",
    }
'''

TEST = r'''from pathlib import Path

def main():
    text = Path("backend/app/main.py").read_text(encoding="utf-8", errors="replace")
    required = [
        "/admin/live-provider-readiness",
        "openai_configured",
        "owner_approved_live_activation",
        "provider_execution_ready",
        "secret_values_exposed",
        "LIVE_PROVIDER_READY",
    ]
    missing = [x for x in required if x not in text]
    if missing:
        raise AssertionError(f"Missing provider readiness route markers: {missing}")
    print("LIVE_PROVIDER_READINESS_ROUTE_TEST_PASSED")

if __name__ == "__main__":
    main()
'''

def backup(path):
    if path.exists():
        BACKUP.mkdir(parents=True, exist_ok=True)
        (BACKUP / path.name).write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")

def main():
    text = MAIN_FILE.read_text(encoding="utf-8", errors="replace")
    if "/admin/live-provider-readiness" not in text:
        backup(MAIN_FILE)
        MAIN_FILE.write_text(text.rstrip() + "\n\n" + ROUTE + "\n", encoding="utf-8")

    backup(TEST_FILE)
    TEST_FILE.write_text(TEST, encoding="utf-8")

    print("LIVE_PROVIDER_READINESS_ROUTE_INSTALLED")
    print("Backup:", BACKUP)
    print("Updated:", MAIN_FILE)
    print("Created:", TEST_FILE)

if __name__ == "__main__":
    main()