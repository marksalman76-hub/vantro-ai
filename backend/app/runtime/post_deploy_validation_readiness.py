from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


POST_DEPLOY_REQUIRED_CHECKS = [
    "api_health",
    "security_headers",
    "admin_auth",
    "run_agent_live_execution",
    "qa_testing_agent",
    "provider_bridge",
    "canonical_agent_identity",
    "persistence",
    "credential_protection",
    "customer_safe_output",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_post_deploy_validation_packet(checks: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    checks = checks or []

    normalised = []
    for check in checks:
        name = str(check.get("name") or "unknown_check")
        passed = bool(check.get("passed", False))
        warning = bool(check.get("warning", False))

        status = "passed" if passed else "warning" if warning else "failed"

        normalised.append({
            "name": name,
            "status": status,
            "passed": passed,
            "warning": warning,
            "details": check.get("details") or {},
            "client_safe": True,
        })

    failed = [c for c in normalised if c["status"] == "failed"]
    warnings = [c for c in normalised if c["status"] == "warning"]

    if failed:
        release_status = "blocked"
        recommendation = "Do not promote this deployment. Review failed checks and rollback if user-facing risk is confirmed."
    elif warnings:
        release_status = "owner_review"
        recommendation = "Deployment may remain live, but owner/admin review is recommended before further changes."
    else:
        release_status = "release_ready"
        recommendation = "Deployment is ready. No blocking validation issues detected."

    return {
        "success": True,
        "post_deploy_validation_ready": True,
        "generated_at": utc_now_iso(),
        "release_status": release_status,
        "recommendation": recommendation,
        "summary": {
            "total_checks": len(normalised),
            "passed": len([c for c in normalised if c["status"] == "passed"]),
            "warnings": len(warnings),
            "failed": len(failed),
        },
        "checks": normalised,
        "governance": {
            "rollback_recommendations_are_advisory_only": True,
            "owner_approval_required_for_release_override": True,
            "no_autonomous_spend_or_scaling": True,
            "client_safe": True,
        },
        "visibility": {
            "credential_values_exposed": False,
            "internal_prompts_exposed": False,
            "backend_config_exposed": False,
            "client_safe": True,
        },
    }


def post_deploy_validation_status() -> Dict[str, Any]:
    return {
        "success": True,
        "post_deploy_validation_readiness_ready": True,
        "required_check_count": len(POST_DEPLOY_REQUIRED_CHECKS),
        "required_checks": POST_DEPLOY_REQUIRED_CHECKS,
        "release_readiness_scoring_enabled": True,
        "rollback_recommendations_advisory_only": True,
        "qa_testing_agent_supported": True,
        "credential_values_exposed": False,
        "client_safe": True,
    }
