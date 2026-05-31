from pathlib import Path
import json

ROOT = Path.cwd()
security_dir = ROOT / "telemetry" / "security"

def read_json(name):
    path = security_dir / name
    if not path.exists():
        return {"success": False, "missing_report": str(path)}
    return json.loads(path.read_text(encoding="utf-8"))

audit = read_json("production-secret-audit-report.json")
redaction = read_json("redaction-verification.json")
token = read_json("token-governance-verification.json")
env = read_json("production-env-validator.json")
provider = read_json("provider-secret-enforcement.json")

phase1 = {
    "success": (
        audit.get("finding_count", 1) == 0
        and redaction.get("success") is True
        and token.get("success") is True
    ),
    "phase": "Phase 1 - Security finalisation",
    "production_rotation_executed": False,
    "owner_approval_required_before_rotation": True,
    "secret_values_exposed": False,
    "audit_finding_count": audit.get("finding_count"),
    "controlled_local_secret_count": audit.get("controlled_local_secret_count"),
    "legacy_reference_count": audit.get("legacy_reference_count"),
    "redaction_passed": redaction.get("success"),
    "token_governance_passed": token.get("success"),
    "production_env_ready": env.get("success"),
    "provider_secret_enforcement_ready": provider.get("success"),
    "phase1_closeout_state": "foundation_complete_rotation_pending" if audit.get("finding_count", 1) == 0 else "review_required",
    "remaining_owner_actions": [
        "rotate production secrets in host providers",
        "set missing production environment variables",
        "confirm rollback values stored safely",
        "run final live production env validation after rotation"
    ],
}

out = security_dir / "phase1-final-completion-verifier.json"
out.write_text(json.dumps(phase1, indent=2), encoding="utf-8")

print("PHASE1_FINAL_COMPLETION_VERIFIER_COMPLETED")
print("PHASE1_CLOSEOUT_STATE:", phase1["phase1_closeout_state"])
print("AUDIT_FINDING_COUNT:", phase1["audit_finding_count"])
print("REDACTION_PASSED:", phase1["redaction_passed"])
print("TOKEN_GOVERNANCE_PASSED:", phase1["token_governance_passed"])
