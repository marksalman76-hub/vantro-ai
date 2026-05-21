from __future__ import annotations

import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple


SECURITY_PROFILE = "priority5_active_security_runtime_v1"

ROOT = Path.cwd()
AUDIT_DIR = ROOT / "data" / "security"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_FILE = AUDIT_DIR / "active_security_events.jsonl"

_RATE_BUCKET: Dict[str, Tuple[int, float]] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _client_ip(request: Any) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
      return forwarded.split(",")[0].strip()
    if request.client:
      return request.client.host
    return "unknown"


def request_fingerprint(request: Any) -> str:
    raw = "|".join([
        _client_ip(request),
        request.headers.get("user-agent", ""),
        request.headers.get("x-tenant-id", ""),
        request.headers.get("x-actor-role", ""),
    ])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def classify_security_event(event_type: str) -> str:
    critical = {
        "credential_exposure_attempt",
        "entitlement_bypass_attempt",
        "owner_approval_bypass_attempt",
        "governance_override_attempt",
        "payment_credit_bypass_attempt",
    }
    high = {
        "admin_route_without_owner_cookie",
        "client_unpaid_agent_attempt",
        "cross_tenant_attempt",
        "one_time_link_reuse",
        "rate_limit_exceeded",
    }
    medium = {
        "missing_client_session",
        "expired_session_reuse",
        "missing_tenant_header",
        "csrf_token_missing",
    }

    if event_type in critical:
        return "critical"
    if event_type in high:
        return "high"
    if event_type in medium:
        return "medium"
    return "low"


def log_security_event(event_type: str, request: Any, extra: Dict[str, Any] | None = None) -> Dict[str, Any]:
    event = {
        "created_at": _now(),
        "security_profile": SECURITY_PROFILE,
        "event_type": event_type,
        "severity": classify_security_event(event_type),
        "path": getattr(request.url, "path", ""),
        "method": getattr(request, "method", ""),
        "client_ip": _client_ip(request),
        "fingerprint": request_fingerprint(request),
        "tenant_id": request.headers.get("x-tenant-id", ""),
        "actor_role": request.headers.get("x-actor-role", ""),
        "user_agent_hash": hashlib.sha256(request.headers.get("user-agent", "").encode("utf-8")).hexdigest()[:16],
        "customer_safe_response_mode": True,
        "secret_values_exposed": False,
        "extra": extra or {},
    }

    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    return event


def rate_limit_check(request: Any) -> Dict[str, Any]:
    limit = int(os.getenv("SECURITY_RATE_LIMIT_PER_MINUTE", "240"))
    window = 60.0
    key = request_fingerprint(request)
    now = time.time()

    count, reset_at = _RATE_BUCKET.get(key, (0, now + window))
    if now > reset_at:
        count = 0
        reset_at = now + window

    count += 1
    _RATE_BUCKET[key] = (count, reset_at)

    allowed = count <= limit

    return {
        "allowed": allowed,
        "limit": limit,
        "count": count,
        "reset_seconds": max(0, int(reset_at - now)),
    }


def csrf_check_required(request: Any) -> bool:
    if os.getenv("SECURITY_CSRF_ENFORCEMENT", "audit").lower() != "enforce":
        return False

    method = getattr(request, "method", "").upper()
    if method not in {"POST", "PUT", "PATCH", "DELETE"}:
        return False

    path = getattr(request.url, "path", "")
    return path.startswith("/api/") or path.startswith("/client")


def csrf_check_passed(request: Any) -> bool:
    token_header = request.headers.get("x-csrf-token", "")
    token_cookie = request.cookies.get("csrf_token", "")
    return bool(token_header and token_cookie and token_header == token_cookie)


def secure_cookie_policy_summary() -> Dict[str, Any]:
    app_env = os.getenv("APP_ENV", os.getenv("ENVIRONMENT", "development")).lower()
    production = app_env in {"prod", "production"}

    return {
        "production_mode_detected": production,
        "secure_cookie_required": production,
        "http_only_required": True,
        "same_site_recommended": "lax",
        "csrf_enforcement_mode": os.getenv("SECURITY_CSRF_ENFORCEMENT", "audit"),
        "rate_limit_per_minute": int(os.getenv("SECURITY_RATE_LIMIT_PER_MINUTE", "240")),
    }


def active_security_readiness() -> Dict[str, Any]:
    return {
        "success": True,
        "security_profile": SECURITY_PROFILE,
        "checked_at": _now(),
        "active_rate_limiting": True,
        "persistent_security_audit_events": True,
        "request_fingerprinting": True,
        "csrf_validation_available": True,
        "csrf_mode": os.getenv("SECURITY_CSRF_ENFORCEMENT", "audit"),
        "secure_cookie_policy": secure_cookie_policy_summary(),
        "audit_file": str(AUDIT_FILE),
        "customer_safe_response_mode": True,
        "secret_values_exposed": False,
    }
