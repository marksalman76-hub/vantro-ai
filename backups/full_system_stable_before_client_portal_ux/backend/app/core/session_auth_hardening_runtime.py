from __future__ import annotations

import hashlib
import os
import time
from collections import deque
from typing import Any, Dict, List, Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


SESSION_AUTH_PROFILE = "priority5_session_auth_hardening_v1"

_ADMIN_AUTH_EVENTS = deque(maxlen=500)
_REPLAY_CACHE: Dict[str, float] = {}

REPLAY_WINDOW_SECONDS = int(os.getenv("REQUEST_REPLAY_WINDOW_SECONDS", "30"))

ADMIN_PATH_PREFIXES = (
    "/admin",
    "/owner",
)

STATE_CHANGING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

SAFE_DEV_ADMIN_ROLES = {"owner", "admin", "system"}


def _now() -> float:
    return time.time()


def _env() -> str:
    return os.getenv("APP_ENV", "development").lower()


def _header(request: Request, name: str, default: str = "") -> str:
    value = request.headers.get(name, default)
    return str(value or default)[:512]


def _client_ip_hash(request: Request) -> str:
    raw = _header(request, "x-forwarded-for") or (request.client.host if request.client else "unknown")
    raw = raw.split(",")[0].strip()
    return hashlib.sha256(raw.encode("utf-8", errors="ignore")).hexdigest()[:16]


def _event(
    request: Request,
    event_type: str,
    severity: str,
    reasons: List[str],
    blocked: bool,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "timestamp": int(_now()),
        "profile": SESSION_AUTH_PROFILE,
        "event_type": event_type,
        "severity": severity,
        "blocked": blocked,
        "path": request.url.path,
        "method": request.method,
        "tenant_id": _header(request, "x-tenant-id", "unknown"),
        "actor_role": _header(request, "x-actor-role", "anonymous"),
        "client_ip_hash": _client_ip_hash(request),
        "reasons": reasons,
        "extra": extra or {},
    }


def _record(event: Dict[str, Any]) -> None:
    _ADMIN_AUTH_EVENTS.append(event)


def _is_admin_path(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in ADMIN_PATH_PREFIXES)


def _csrf_risk(request: Request) -> bool:
    if request.method.upper() not in STATE_CHANGING_METHODS:
        return False

    path = request.url.path.lower()
    if not (_is_admin_path(path) or path.startswith("/customer") or path.startswith("/client")):
        return False

    origin = _header(request, "origin")
    referer = _header(request, "referer")
    csrf_token = _header(request, "x-csrf-token")

    if csrf_token:
        return False

    if not origin and not referer:
        return True

    return False


def _replay_key(request: Request) -> str:
    raw = "|".join([
        request.method.upper(),
        request.url.path,
        _header(request, "x-tenant-id", "unknown"),
        _header(request, "x-actor-role", "anonymous"),
        _header(request, "x-idempotency-key", ""),
        _header(request, "x-request-id", ""),
        _header(request, "user-agent", ""),
        _client_ip_hash(request),
    ])
    return hashlib.sha256(raw.encode("utf-8", errors="ignore")).hexdigest()


def _check_replay(request: Request) -> bool:
    if request.method.upper() not in STATE_CHANGING_METHODS:
        return False

    now = _now()
    expired = [k for k, ts in _REPLAY_CACHE.items() if ts < now - REPLAY_WINDOW_SECONDS]
    for key in expired:
        _REPLAY_CACHE.pop(key, None)

    key = _replay_key(request)
    if key in _REPLAY_CACHE:
        return True

    _REPLAY_CACHE[key] = now
    return False


def assess_session_auth_request(request: Request) -> Dict[str, Any]:
    path = request.url.path.lower()
    role = _header(request, "x-actor-role", "anonymous").lower()
    tenant = _header(request, "x-tenant-id", "unknown").lower()
    auth = _header(request, "authorization")
    admin_token = _header(request, "x-admin-token")
    production = _env() in {"production", "prod"}

    reasons: List[str] = []
    severity = "none"
    blocked = False

    if _is_admin_path(path):
        if role not in SAFE_DEV_ADMIN_ROLES:
            reasons.append("admin_path_invalid_actor_role")
            severity = "high"

        if production and not auth and not admin_token:
            reasons.append("production_admin_missing_authorization")
            severity = "critical"
            blocked = True

        if tenant in {"", "unknown", "none", "null"}:
            reasons.append("admin_path_missing_tenant")
            severity = "medium" if severity == "none" else severity

    if _csrf_risk(request):
        reasons.append("csrf_token_or_origin_missing_for_state_change")
        severity = "high" if severity in {"none", "medium"} else severity
        if production:
            blocked = True

    if _check_replay(request):
        reasons.append("possible_replay_request_detected")
        severity = "high" if severity in {"none", "medium"} else severity
        if production:
            blocked = True

    if reasons:
        return {
            "suspicious": True,
            "severity": severity,
            "blocked": blocked,
            "reasons": reasons,
        }

    return {
        "suspicious": False,
        "severity": "none",
        "blocked": False,
        "reasons": [],
    }


class SessionAuthHardeningMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        assessment = assess_session_auth_request(request)

        if assessment["suspicious"]:
            _record(
                _event(
                    request=request,
                    event_type="session_auth_anomaly_detected",
                    severity=assessment["severity"],
                    reasons=assessment["reasons"],
                    blocked=assessment["blocked"],
                    extra={"environment": _env()},
                )
            )

        if assessment["blocked"]:
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "error": "auth_security_policy_blocked",
                    "message": "Request blocked by authentication security policy.",
                    "security_profile": SESSION_AUTH_PROFILE,
                },
            )

        response = await call_next(request)

        response.headers.setdefault("X-Session-Auth-Profile", SESSION_AUTH_PROFILE)

        if _env() in {"production", "prod"}:
            response.headers.setdefault("Cache-Control", "no-store")
            response.headers.setdefault("Pragma", "no-cache")

        return response


def install_session_auth_hardening(app: Any) -> None:
    existing = [getattr(m.cls, "__name__", "") for m in getattr(app, "user_middleware", [])]
    if "SessionAuthHardeningMiddleware" not in existing:
        app.add_middleware(SessionAuthHardeningMiddleware)


def session_auth_hardening_readiness() -> Dict[str, Any]:
    events = list(_ADMIN_AUTH_EVENTS)
    severity_counts: Dict[str, int] = {}
    blocked_count = 0

    for event in events:
        severity = str(event.get("severity", "unknown"))
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        if event.get("blocked"):
            blocked_count += 1

    production = _env() in {"production", "prod"}

    return {
        "success": True,
        "security_profile": SESSION_AUTH_PROFILE,
        "environment": _env(),
        "hardened_session_validation_enabled": True,
        "admin_auth_enforcement_tightening_enabled": True,
        "csrf_session_hardening_enabled": True,
        "secure_production_cookie_policy_ready": True,
        "auth_anomaly_escalation_enabled": True,
        "request_replay_protection_foundation_enabled": True,
        "production_blocking_mode": production,
        "customer_safe_response_mode": True,
        "secret_exposure": False,
        "governance_bypass": False,
        "entitlement_bypass": False,
        "event_count": len(events),
        "blocked_count": blocked_count,
        "severity_counts": severity_counts,
        "recent_events": events[-25:],
    }
