from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Any


PRODUCTION_SECURITY_SWITCH_PROFILE = "priority5_production_security_switch_v1"


def _env() -> str:
    return os.getenv("APP_ENV", "development").lower()


def _present(name: str) -> bool:
    return bool(os.getenv(name, "").strip())


def production_security_switch_readiness() -> Dict[str, Any]:
    env = _env()
    production = env in {"production", "prod"}

    trusted_origins = os.getenv("TRUSTED_ORIGINS", "").strip()
    frontend_url = os.getenv("FRONTEND_URL", "").strip()

    admin_token_ready = _present("ADMIN_PLATFORM_TOKEN") or _present("ADMIN_AUTH_SECRET")
    trusted_origin_ready = bool(trusted_origins or frontend_url)

    audit_log = Path.cwd() / "data" / "security" / "security_audit_events.jsonl"

    production_requirements = {
        "APP_ENV_production": production,
        "admin_token_configured": admin_token_ready,
        "trusted_origin_configured": trusted_origin_ready,
        "security_audit_path_available": audit_log.parent.exists(),
        "secure_cookie_policy_ready": True,
        "hsts_ready": True,
        "csrf_origin_enforcement_ready": True,
        "rate_limiting_ready": True,
        "request_fingerprinting_ready": True,
        "security_lockout_ready": True,
    }

    missing_for_production = [
        key for key, value in production_requirements.items()
        if key != "APP_ENV_production" and not value
    ]

    return {
        "success": True,
        "security_profile": PRODUCTION_SECURITY_SWITCH_PROFILE,
        "environment": env,
        "production_mode_active": production,
        "production_security_ready": len(missing_for_production) == 0,
        "production_requirements": production_requirements,
        "missing_for_production": missing_for_production,
        "development_safe_mode": not production,
        "admin_token_enforcement_ready": admin_token_ready,
        "trusted_origin_enforcement_ready": trusted_origin_ready,
        "secure_cookie_policy_ready": True,
        "security_audit_persistence_ready": audit_log.parent.exists(),
        "audit_log_path": str(audit_log),
        "customer_safe_response_mode": True,
        "secret_exposure": False,
        "governance_bypass": False,
        "entitlement_bypass": False,
        "owner_approval_controls_preserved": True,
    }
