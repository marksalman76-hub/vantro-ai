from pathlib import Path
import json
import sys

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))

from backend.app.core.secure_runtime_config import production_secret_readiness

report = production_secret_readiness()

out_dir = ROOT / "telemetry" / "security"
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "runtime-secret-readiness.json").write_text(
    json.dumps(report, indent=2),
    encoding="utf-8",
)

print("RUNTIME_SECRET_READINESS_CHECK_COMPLETED")
print("SECRET_VALUES_EXPOSED:false")
print("PRESENT_COUNT:", report["present_count"])
print("MISSING_COUNT:", len(report["missing"]))

if not report["success"]:
    print("RUNTIME_SECRET_READINESS_NOT_FULLY_CONFIGURED")
