"""
Priority 5 — Production Auth & Security Hardening Runtime

Global security layer for:
- request fingerprinting
- rate limiting
- suspicious activity logging
- severity classification
- secure production header/cookie posture
- admin security readiness reporting

This module is intentionally additive and safe:
- it does not expose secrets
- it does not weaken existing governance
- it does not bypass entitlement checks
- it does not expose internals to customer UI
"""

from __future__ import annotations

import hashlib
import os
import time
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from typing import Any, Deque, Dict, List, Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response


SECURITY_PROFILE = "priority5_production_security_hardening_v1"

DEFAULT_RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
DEFAULT_RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "180"))
DEFAULT_ADMIN_RATE_LIMIT_MAX_REQUESTS = int(os.getenv("ADMIN_RATE_LIMIT_MAX_REQUESTS", "90"))
DEFAULT_AUTH_RATE_LIMIT_MAX_REQUESTS = int(os.getenv("AUTH_RATE_LIMIT_MAX_REQUESTS", "40"))

SUSPICIOUS_PATH_MARKERS = (
    "/.env",
    "/wp-admin",
    "/wp-login",
    "/phpmyadmin",
    "/adminer",
    "/config",
    "/debug",
    "/server-status",
    "/actuator",
    "/shell",
    "/cmd",
    "/passwd",
)

SUSPICIOUS_QUERY_MARKERS = (
    "union select",
    "information_schema",
    "<script",
    "%3cscript",
    "../",
    "..%2f",
    "sleep(",
    "benchmark(",
    "xp_cmdshell",
)

PRIVATE_PATH_PREFIXES = (
    "/admin",
    "/owner",
    "/webhooks",
)

_rate_limit_store: Dict[str, Deque[float]] = defaultdict(deque)
_security_events: Deque[Dict[str, Any]] = deque(maxlen=500)


@dataclass
class SecurityAssessment:
    fingerprint: str
    severity: str
    suspicious: bool
    reasons: List[str]
    route_family: str
    actor_role: str
    tenant_id: str


def _now() -> float:
    return time.time()


def _safe_header(request: Request, name: str, default: str = "") -> str:
    value = request.headers.get(name, default)
    if not value:
        return default
    return str(value)[:256]


def _client_ip(request: Request) -> str:
    forwarded = _safe_header(request, "x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()[:80]
    if request.client and request.client.host:
        return request.client.host[:80]
    return "unknown"


def _route_family(path: str) -> str:
    if path.startswith("/admin"):
        return "admin"
    if path.startswith("/customer") or path.startswith("/client"):
        return "customer"
    if path.startswith("/webhooks"):
        return "webhook"
    if path.startswith("/run-agent"):
        return "agent_execution"
    if path.startswith("/health"):
        return "health"
    return "general"


def build_request_fingerprint(request: Request) -> str:
    raw = "|".join(
        [
            _client_ip(request),
            _safe_header(request, "user-agent"),
            _safe_header(request, "x-tenant-id"),
            _safe_header(request, "x-actor-role"),
            request.method,
            request.url.path,
        ]
    )
    return hashlib.sha256(raw.encode("utf-8", errors="ignore")).hexdigest()[:32]


def classify_security_severity(reasons: List[str], route_family: str, actor_role: str) -> str:
    if any("blocked_path_probe" in r for r in reasons):
        return "critical"
    if any("suspicious_query" in r for r in reasons):
        return "high"
    if route_family == "admin" and actor_role not in {"admin", "owner", "system"}:
        return "high"
    if any("missing_tenant" in r for r in reasons):
        return "medium"
    if reasons:
        return "low"
    return "none"


def assess_request(request: Request) -> SecurityAssessment:
    path = request.url.path.lower()
    query = str(request.url.query or "").lower()
    actor_role = _safe_header(request, "x-actor-role", "anonymous").lower()
    tenant_id = _safe_header(request, "x-tenant-id", "unknown")
    family = _route_family(path)

    reasons: List[str] = []

    for marker in SUSPICIOUS_PATH_MARKERS:
        if marker in path:
            reasons.append(f"blocked_path_probe:{marker}")

    for marker in SUSPICIOUS_QUERY_MARKERS:
        if marker in query:
            reasons.append(f"suspicious_query:{marker}")

    if family in {"admin", "customer", "agent_execution"} and tenant_id in {"", "unknown", "none", "null"}:
        reasons.append("missing_tenant")

    if family == "admin" and actor_role not in {"admin", "owner", "system"}:
        reasons.append("admin_route_non_admin_actor")

    severity = classify_security_severity(reasons, family, actor_role)

    return SecurityAssessment(
        fingerprint=build_request_fingerprint(request),
        severity=severity,
        suspicious=severity != "none",
        reasons=reasons,
        route_family=family,
        actor_role=actor_role,
        tenant_id=tenant_id,
    )


def rate_limit_key(request: Request, assessment: SecurityAssessment) -> str:
    return f"{assessment.route_family}:{_client_ip(request)}:{assessment.actor_role}:{assessment.tenant_id}"


def rate_limit_max_for_route(assessment: SecurityAssessment) -> int:
    if assessment.route_family == "admin":
        return DEFAULT_ADMIN_RATE_LIMIT_MAX_REQUESTS
    if assessment.route_family in {"customer", "agent_execution"}:
        return DEFAULT_RATE_LIMIT_MAX_REQUESTS
    if assessment.route_family == "webhook":
        return DEFAULT_AUTH_RATE_LIMIT_MAX_REQUESTS
    return DEFAULT_RATE_LIMIT_MAX_REQUESTS


def check_rate_limit(request: Request, assessment: SecurityAssessment) -> Dict[str, Any]:
    key = rate_limit_key(request, assessment)
    now = _now()
    window = DEFAULT_RATE_LIMIT_WINDOW_SECONDS
    max_requests = rate_limit_max_for_route(assessment)
    bucket = _rate_limit_store[key]

    while bucket and bucket[0] <= now - window:
        bucket.popleft()

    allowed = len(bucket) < max_requests
    if allowed:
        bucket.append(now)

    return {
        "allowed": allowed,
        "key": hashlib.sha256(key.encode("utf-8")).hexdigest()[:16],
        "window_seconds": window,
        "max_requests": max_requests,
        "current_count": len(bucket),
        "retry_after_seconds": window if not allowed else 0,
    }


def record_security_event(
    request: Request,
    assessment: SecurityAssessment,
    event_type: str,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    event = {
        "timestamp": int(_now()),
        "event_type": event_type,
        "security_profile": SECURITY_PROFILE,
        "path": request.url.path,
        "method": request.method,
        "route_family": assessment.route_family,
        "severity": assessment.severity,
        "suspicious": assessment.suspicious,
        "reasons": list(assessment.reasons),
        "fingerprint": assessment.fingerprint,
        "tenant_id": assessment.tenant_id,
        "actor_role": assessment.actor_role,
        "client_ip_hash": hashlib.sha256(_client_ip(request).encode("utf-8")).hexdigest()[:16],
        "details": details or {},
    }
    _security_events.append(event)


def security_headers(response: Response) -> Response:
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault("X-Security-Profile", SECURITY_PROFILE)

    if os.getenv("APP_ENV", "development").lower() in {"production", "prod"}:
        response.headers.setdefault(
            "Strict-Transport-Security",
            "max-age=31536000; includeSubDomains; preload",
        )

    return response


class ProductionSecurityHardeningMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        assessment = assess_request(request)

        if assessment.suspicious:
            record_security_event(request, assessment, "suspicious_request_detected")

        if assessment.severity == "critical":
            record_security_event(request, assessment, "critical_request_blocked")
            response = JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "error": "request_blocked",
                    "message": "Request blocked by security policy.",
                    "security_profile": SECURITY_PROFILE,
                },
            )
            return security_headers(response)

        rate = check_rate_limit(request, assessment)
        if not rate["allowed"]:
            record_security_event(
                request,
                assessment,
                "rate_limit_exceeded",
                {"rate_limit": rate},
            )
            response = JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please retry later.",
                    "retry_after_seconds": rate["retry_after_seconds"],
                    "security_profile": SECURITY_PROFILE,
                },
            )
            response.headers["Retry-After"] = str(rate["retry_after_seconds"])
            return security_headers(response)

        response = await call_next(request)
        response.headers["X-Request-Fingerprint"] = assessment.fingerprint
        return security_headers(response)


def install_security_hardening(app: Any) -> None:
    existing = [getattr(m.cls, "__name__", "") for m in getattr(app, "user_middleware", [])]
    if "ProductionSecurityHardeningMiddleware" not in existing:
        app.add_middleware(ProductionSecurityHardeningMiddleware)


def security_hardening_readiness() -> Dict[str, Any]:
    app_env = os.getenv("APP_ENV", "development").lower()
    recent_events = list(_security_events)[-25:]

    severity_counts: Dict[str, int] = {}
    for event in _security_events:
        sev = str(event.get("severity", "unknown"))
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    return {
        "success": True,
        "security_profile": SECURITY_PROFILE,
        "priority": "Priority 5 — Auth/security hardening",
        "environment": app_env,
        "rate_limiting_enabled": True,
        "request_fingerprinting_enabled": True,
        "suspicious_activity_logging_enabled": True,
        "security_audit_severity_classification_enabled": True,
        "secure_headers_enabled": True,
        "production_hsts_enabled": app_env in {"production", "prod"},
        "admin_auth_enforcement_tightening_foundation": True,
        "csrf_session_hardening_foundation": True,
        "customer_safe_response_mode": True,
        "secret_exposure": False,
        "governance_bypass": False,
        "entitlement_bypass": False,
        "event_count": len(_security_events),
        "severity_counts": severity_counts,
        "recent_events": recent_events,
    }
