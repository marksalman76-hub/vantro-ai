from pathlib import Path
from datetime import datetime
import json

ROOT = Path.cwd()
ops = ROOT / "telemetry" / "operations"

required_reports = [
    "operational-monitoring-runtime.json",
    "incident-response-runtime.json",
    "provider-failover-runtime.json",
    "postgres-backup-restore-runtime.json",
    "live-operational-telemetry.json",
    "provider-health-scoring.json",
    "queue-degradation-detection.json",
    "incident-packet-runtime.json",
    "alert-escalation-pipeline.json",
    "circuit-breaker-runtime.json",
    "restore-simulation-runtime.json",
    "operational-persistence-runtime.json",
    "provider-recovery-scoring.json",
    "incident-history-registry.json",
    "backup-manifest-runtime.json",
    "operational-dashboard-feed.json",
    "runtime-sla-scoring.json",
]

missing = []
failed = []

for name in required_reports:
    path = ops / name
    if not path.exists():
        missing.append(name)
        continue
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("success") is not True:
        failed.append(name)

report = {
    "success": not missing and not failed,
    "phase": "Phase 2 - Monitoring & incident operations",
    "phase2_closeout_state": "foundation_complete_live_provisioning_pending" if not missing and not failed else "review_required",
    "required_reports": len(required_reports),
    "missing_reports": missing,
    "failed_reports": failed,
    "live_external_actions_enabled": False,
    "remaining_owner_actions": [
        "provision production secrets",
        "connect live monitoring provider if required",
        "enable live backup execution after owner approval",
        "run final live incident and failover validation after provider provisioning"
    ],
    "generated_at": datetime.utcnow().isoformat()
}

(ops / "phase2-completion-verifier.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

print("PHASE2_COMPLETION_VERIFIER_READY")
print("PHASE2_CLOSEOUT_STATE:", report["phase2_closeout_state"])
print("MISSING_REPORTS:", len(missing))
print("FAILED_REPORTS:", len(failed))
