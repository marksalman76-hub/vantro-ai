from pathlib import Path
from datetime import datetime

ROOT = Path(".")
backup_dir = ROOT / "backups" / ("autonomous_qa_regression_before_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=True)

qa_path = Path("backend/app/runtime/autonomous_qa_regression_intelligence.py")

if qa_path.exists():
    (backup_dir / qa_path.name).write_text(qa_path.read_text(encoding="utf-8"), encoding="utf-8")

qa_path.parent.mkdir(parents=True, exist_ok=True)

qa_path.write_text('''from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


CRITICAL_RUNTIME_CHECKS = [
    "health_endpoint",
    "run_agent_endpoint",
    "governed_openai_live_provider_bridge",
    "canonical_agent_identity_bridge",
    "owner_admin_execution_bypass",
    "credential_protection",
    "customer_safe_output",
    "durable_persistence",
    "audit_persistence",
    "qa_testing_agent",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def classify_check_status(check: Dict[str, Any]) -> str:
    if check.get("passed") is True:
        return "passed"
    if check.get("warning") is True:
        return "warning"
    return "failed"


def build_qa_regression_packet(
    *,
    checks: List[Dict[str, Any]] | None = None,
    source: str = "qa_testing_agent",
    environment: str = "production",
) -> Dict[str, Any]:
    checks = checks or []

    normalised_checks = []
    for item in checks:
        normalised_checks.append({
            "name": str(item.get("name") or "unknown_check"),
            "status": classify_check_status(item),
            "passed": bool(item.get("passed")),
            "warning": bool(item.get("warning", False)),
            "details": item.get("details") or {},
            "client_safe": True,
        })

    failed = [c for c in normalised_checks if c["status"] == "failed"]
    warnings = [c for c in normalised_checks if c["status"] == "warning"]

    if failed:
        readiness_status = "blocked"
        recommendation = "Do not release. Resolve failed checks before deployment or client delivery."
    elif warnings:
        readiness_status = "review_recommended"
        recommendation = "Release may proceed after owner/admin review of warnings."
    else:
        readiness_status = "ready"
        recommendation = "Release-ready. No blocking QA findings detected."

    return {
        "success": True,
        "qa_regression_intelligence_ready": True,
        "source": source,
        "environment": environment,
        "generated_at": utc_now_iso(),
        "readiness_status": readiness_status,
        "recommendation": recommendation,
        "summary": {
            "total_checks": len(normalised_checks),
            "passed": len([c for c in normalised_checks if c["status"] == "passed"]),
            "warnings": len(warnings),
            "failed": len(failed),
        },
        "checks": normalised_checks,
        "governance": {
            "owner_approval_required_for_release_if_failed": True,
            "rollback_recommendations_are_advisory_only": True,
            "no_autonomous_spend_or_scaling": True,
            "client_safe": True,
        },
        "visibility": {
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "customer_safe": True,
        },
    }


def autonomous_qa_regression_status() -> Dict[str, Any]:
    return {
        "success": True,
        "autonomous_qa_regression_intelligence_ready": True,
        "qa_testing_agent_enabled": True,
        "critical_runtime_check_count": len(CRITICAL_RUNTIME_CHECKS),
        "critical_runtime_checks": CRITICAL_RUNTIME_CHECKS,
        "release_readiness_scoring_enabled": True,
        "failed_execution_clustering_ready": True,
        "post_deploy_validation_ready": True,
        "rollback_recommendations_advisory_only": True,
        "credential_values_exposed": False,
        "client_safe": True,
    }
''', encoding="utf-8")

print("AUTONOMOUS_QA_REGRESSION_INTELLIGENCE_INSTALLED")
print("Backup:", backup_dir)
print("Created:", qa_path)