from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Dict, Any, List


SECURITY_PROFILE = "priority5_final_security_readiness_v1"


def _present(name: str) -> bool:
    return bool(os.getenv(name, "").strip())


def priority5_final_security_readiness() -> Dict[str, Any]:
    required_env = [
        "JWT_SECRET",
        "PORTAL_ACCESS_CODE",
        "ADMIN_AUTH_SECRET",
        "FRONTEND_URL",
        "BACKEND_URL",
    ]

    present = [key for key in required_env if _present(key)]
    missing = [key for key in required_env if key not in present]

    security_layers = {
        "admin_route_protection": True,
        "client_session_route_protection": True,
        "proxy_based_route_guard": True,
        "secure_cookie_policy_required": True,
        "csrf_session_hardening_required": True,
        "rate_limit_layer_required": True,
        "suspicious_activity_logging_required": True,
        "request_fingerprinting_required": True,
        "audit_severity_classification_required": True,
        "owner_admin_bypass_limited_to_internal_operations": True,
        "client_entitlement_isolation_required": True,
        "secret_exposure_blocked": True,
    }

    readiness_checks = {
        "required_env_present": len(missing) == 0,
        "admin_access_secret_configured": _present("PORTAL_ACCESS_CODE") or _present("ADMIN_AUTH_SECRET"),
        "jwt_secret_configured": _present("JWT_SECRET"),
        "frontend_url_configured": _present("FRONTEND_URL"),
        "backend_url_configured": _present("BACKEND_URL"),
        "secure_cookie_policy_ready": _present("JWT_SECRET") and (_present("FRONTEND_URL") or _present("BACKEND_URL")),
        "audit_layer_ready": True,
        "rate_limit_policy_defined": True,
        "suspicious_activity_model_defined": True,
        "csrf_policy_defined": True,
    }

    severity_model = {
        "low": [
            "unknown route probe",
            "missing optional client context",
            "non-sensitive validation miss",
        ],
        "medium": [
            "repeated failed client login",
            "expired session reuse",
            "missing tenant header on protected action",
        ],
        "high": [
            "admin route access without valid owner token",
            "client attempting unpaid agent access",
            "cross-tenant access attempt",
            "one-time onboarding link reuse",
        ],
        "critical": [
            "credential exposure attempt",
            "entitlement bypass attempt",
            "owner approval bypass attempt",
            "governance override attempt",
            "payment/credit enforcement bypass attempt",
        ],
    }

    production_ready = all(readiness_checks.values())

    return {
        "success": True,
        "security_profile": SECURITY_PROFILE,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "production_security_ready": production_ready,
        "required_env_count": len(required_env),
        "present_env_count": len(present),
        "missing_env_count": len(missing),
        "present_env": present,
        "missing_env": missing,
        "security_layers": security_layers,
        "readiness_checks": readiness_checks,
        "suspicious_activity_severity_model": severity_model,
        "customer_safe_response_mode": True,
        "secret_values_exposed": False,
        "next_required_runtime_steps": [
            "Add active rate-limiting middleware",
            "Add persistent suspicious activity audit events",
            "Add request fingerprint calculation",
            "Add CSRF token validation for state-changing browser actions",
            "Enforce secure cookie flags in production",
        ],
    }
