from pathlib import Path
from datetime import datetime
import json

ROOT = Path.cwd()
ops = ROOT / "telemetry" / "load-testing"

required = [
    "load-test-dryrun-runtime.json",
    "concurrency-simulation-runtime.json",
    "provider-saturation-governance.json",
    "worker-pressure-telemetry.json",
    "retry-storm-prevention.json",
    "concurrency-sla-scoring.json"
]

missing = []
failed = []

for name in required:
    path = ops / name
    if not path.exists():
        missing.append(name)
        continue
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("success") is not True:
        failed.append(name)

report = {
    "success": not missing and not failed,
    "phase": "Phase 3 - Load testing & scaling validation",
    "phase3_closeout_state": "foundation_complete_real_load_tests_pending" if not missing and not failed else "review_required",
    "required_reports": len(required),
    "missing_reports": missing,
    "failed_reports": failed,
    "production_high_volume_load_executed": False,
    "remaining_owner_actions": [
        "approve safe live load test window",
        "confirm monitoring active during test",
        "confirm rollback controls",
        "run controlled k6 tests",
        "review provider saturation and cost controls"
    ],
    "generated_at": datetime.utcnow().isoformat()
}

(ops / "phase3-readiness-verifier.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

print("PHASE3_READINESS_VERIFIER_READY")
print("PHASE3_CLOSEOUT_STATE:", report["phase3_closeout_state"])
print("MISSING_REPORTS:", len(missing))
print("FAILED_REPORTS:", len(failed))
