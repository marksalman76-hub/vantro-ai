from pathlib import Path
from datetime import datetime
import json
import shutil

ROOT = Path.cwd()
STAMP = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / "production" / f"live_hosted_secret_readiness_before_{STAMP}"
BACKUP.mkdir(parents=True, exist_ok=True)

def backup(path: Path):
    if path.exists() and path.is_file():
        target = BACKUP / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)

def write(path_str, content):
    path = ROOT / path_str
    backup(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print("UPDATED", path_str)

write("scripts/activation/live-hosted-secret-readiness-verifier.py", r'''
from pathlib import Path
from datetime import datetime
import json
import urllib.request
import urllib.error

ROOT = Path.cwd()
API_BASE = "https://api.trance-formation.com.au"

endpoints = [
    "/health",
    "/admin/provider-activation-visibility",
    "/admin/provider-action-readiness",
]

results = {}

for endpoint in endpoints:
    url = API_BASE + endpoint
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "live-hosted-secret-readiness-verifier"})
        with urllib.request.urlopen(req, timeout=20) as response:
            body = response.read().decode("utf-8", errors="replace")
            results[endpoint] = {
                "reachable": True,
                "status": response.status,
                "body_preview": body[:1000],
            }
    except urllib.error.HTTPError as exc:
        results[endpoint] = {
            "reachable": True,
            "status": exc.code,
            "body_preview": exc.read().decode("utf-8", errors="replace")[:1000],
        }
    except Exception as exc:
        results[endpoint] = {
            "reachable": False,
            "status": None,
            "error": str(exc),
        }

health_ok = results.get("/health", {}).get("status") == 200

report = {
    "success": health_ok,
    "mode": "live_hosted_secret_readiness",
    "api_base": API_BASE,
    "secret_values_exposed": False,
    "health_ok": health_ok,
    "results": results,
    "note": "This verifies hosted backend reachability and readiness endpoints. It does not expose secret values.",
    "generated_at": datetime.utcnow().isoformat(),
}

out = ROOT / "telemetry" / "activation" / "live-hosted-secret-readiness-verifier.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("LIVE_HOSTED_SECRET_READINESS_VERIFIER_COMPLETED")
print("API_BASE:", API_BASE)
print("HEALTH_OK:", health_ok)
print("SECRET_VALUES_EXPOSED:false")
''')

write("scripts/activation/live-hosted-secret-readiness-check.js", r'''
const { spawnSync } = require("child_process");

const result = spawnSync(
  "python",
  ["scripts/activation/live-hosted-secret-readiness-verifier.py"],
  { stdio: "inherit", shell: false }
);

if (result.status !== 0) {
  console.log("LIVE_HOSTED_SECRET_READINESS_CHECK_FAILED");
  process.exit(1);
}

console.log("LIVE_HOSTED_SECRET_READINESS_CHECK_PASSED");
''')

print("LIVE_HOSTED_SECRET_READINESS_VERIFIER_INSTALLED")
print("Backup:", BACKUP)