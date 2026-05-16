from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
TEST = ROOT / "test_step239_commercial_launch_readiness_lock.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"test_step239_before_step241_env_load_{timestamp}.py"
backup.write_text(TEST.read_text(encoding="utf-8"), encoding="utf-8")

TEST.write_text(r'''
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path.cwd()
ENV_FILES = [
    ROOT / ".env.local",
    ROOT / ".env",
]

for env_file in ENV_FILES:
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            clean = line.strip()
            if not clean or clean.startswith("#") or "=" not in clean:
                continue

            key, value = clean.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if key and key not in os.environ:
                os.environ[key] = value

matrix_path = ROOT / "backend" / "app" / "data" / "step239_commercial_launch_readiness_matrix.json"
matrix = json.loads(matrix_path.read_text(encoding="utf-8"))

required_env_presence_only = {
    "STRIPE_SECRET_KEY": bool(os.getenv("STRIPE_SECRET_KEY")),
    "STRIPE_WEBHOOK_SECRET": bool(os.getenv("STRIPE_WEBHOOK_SECRET")),
    "STRIPE_PRICE_STARTER_MONTHLY": bool(os.getenv("STRIPE_PRICE_STARTER_MONTHLY")),
    "STRIPE_PRICE_GROWTH_MONTHLY": bool(os.getenv("STRIPE_PRICE_GROWTH_MONTHLY")),
    "STRIPE_PRICE_PRO_MONTHLY": bool(os.getenv("STRIPE_PRICE_PRO_MONTHLY")),
}


def backend_get(path: str):
    req = urllib.request.Request(
        "http://127.0.0.1:8000" + path,
        headers={
            "x-actor-role": "owner",
            "x-tenant-id": "owner",
        },
        method="GET",
    )

    with urllib.request.urlopen(req, timeout=30) as res:
        return res.status, json.loads(res.read().decode("utf-8"))


recovery_status, recovery = backend_get("/admin/operations/recovery-summary")
artifacts_status, artifacts = backend_get("/admin/operations/artifacts?limit=5")

combined = json.dumps({
    "matrix": matrix,
    "recovery": recovery,
    "artifacts": artifacts,
}).lower()

checks = {
    "matrix_success": matrix.get("success") is True,
    "commercial_launch_locked": matrix.get("status") == "commercial_launch_readiness_locked",
    "launch_readiness_all_true": all(matrix.get("launch_readiness", {}).values()),
    "commercial_requirements_all_true": all(matrix.get("commercial_requirements", {}).values()),
    "core_platform_ready": matrix.get("launch_gate", {}).get("core_platform_ready") is True,
    "commercial_beta_ready": matrix.get("launch_gate", {}).get("commercial_beta_ready") is True,
    "must_do_items_present": len(matrix.get("production_must_do_before_public_launch", [])) >= 5,
    "stripe_core_env_present": all(required_env_presence_only.values()),
    "backend_recovery_route_ok": recovery_status == 200 and recovery.get("success") is True,
    "backend_artifacts_route_ok": artifacts_status == 200 and artifacts.get("success") is True,
    "no_secret_values_exposed": all(secret not in combined for secret in [
        "sk_live_",
        "sk_test_",
        "sk-",
        "whsec_",
        "postgresql://",
        "ecomagentsecure",
    ]),
}

print("STEP_241_ENV_LOADED_FINAL_COMMERCIAL_LOCK_RESULTS")
for name, passed in checks.items():
    print(name, passed)

print("env_presence_only", required_env_presence_only)

failed = [name for name, passed in checks.items() if not passed]

print("RUNNING_FINAL_CORE_REGRESSION")
regression = subprocess.run(
    [sys.executable, "test_step215_launch_critical_regression_runner.py"],
    text=True,
)
print("final_core_regression_exit_code", regression.returncode)

if regression.returncode != 0:
    failed.append("final_core_regression")

if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_241_ENV_LOADED_FINAL_COMMERCIAL_LOCK_OK")
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_241_ENV_LOADED_FINAL_COMMERCIAL_LOCK_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {TEST}")
print("STEP_241_OK")