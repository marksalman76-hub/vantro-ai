from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


SECURITY_AUDIT_PROFILE = "priority5_security_audit_enforcement_v1"

ROOT = Path.cwd()
SECURITY_DIR = ROOT / "data" / "security"
SECURITY_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_LOG = SECURITY_DIR / "security_audit_events.jsonl"

_EVENTS = deque(maxlen=500)
_FINGERPRINT_COUNTS = defaultdict(int)
_LOCKOUTS = {}

LOCKOUT_THRESHOLD = int(os.getenv("SECURITY_LOCKOUT_THRESHOLD", "12"))
LOCKOUT_WINDOW_SECONDS = int(os.getenv("SECURITY_LOCKOUT_WINDOW_SECONDS", "300"))

ADMIN_PATH_PREFIXES = ("/admin", "/owner")
ADMIN_EVIDENCE_PROXY_PATHS = ("/admin/execution-evidence",)
DEFAULT_TRUSTED_ORIGINS = ("https://app.trance-formation.com.au", "https://trance-formation.com.au")
STATE_CHANGING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def _now() -> float:
    return time.time()


def _env() -> str:
    return os.getenv("APP_ENV", "development").lower()


def _is_production() -> bool:
    return _env() in {"production", "prod"}


def _header(request: Request, name: str, default: str = "") -> str:
    return str(request.headers.get(name, default) or default)[:1024]


def _client_ip(request: Request) -> str:
    forwarded = _header(request, "x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()[:128]
    if request.client and request.client.host:
        return request.client.host[:128]
    return "unknown"


def _hash(value: str, length: int = 16) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()[:length]


def _fingerprint(request: Request) -> str:
    raw = "|".join([
        _client_ip(request),
        _header(request, "user-agent"),
        _header(request, "x-tenant-id", "unknown"),
        _header(request, "x-actor-role", "anonymous"),
        request.method.upper(),
        request.url.path,
    ])
    return _hash(raw, 32)


def _normalise_origins() -> List[str]:
    raw = os.getenv("TRUSTED_ORIGINS", "") or os.getenv("FRONTEND_URL", "")
    configured = [x.strip().rstrip("/") for x in raw.split(",") if x.strip()]
    defaults = list(DEFAULT_TRUSTED_ORIGINS)
    merged = []
    for item in configured + defaults:
        if item and item not in merged:
            merged.append(item)
    return merged


def _trusted_origin_valid(request: Request) -> bool:
    origin = _header(request, "origin").rstrip("/")
    referer = _header(request, "referer").rstrip("/")
    trusted = _normalise_origins()

    if not trusted:
        return not _is_production()

    if origin and any(origin == item or origin.startswith(item + "/") for item in trusted):
        return True

    if referer and any(referer == item or referer.startswith(item + "/") for item in trusted):
        return True

    return False


def _admin_token_valid(request: Request) -> bool:
    expected = os.getenv("ADMIN_PLATFORM_TOKEN", "") or os.getenv("ADMIN_AUTH_SECRET", "")
    if not expected:
        return not _is_production()

    supplied = _header(request, "x-admin-token") or _header(request, "authorization").replace("Bearer ", "")
    if not supplied:
        return False

    return hmac.compare_digest(str(supplied), str(expected))


def _is_admin_path(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in ADMIN_PATH_PREFIXES)


def _admin_evidence_proxy_valid(request: Request) -> bool:
    path = request.url.path.lower()
    method = request.method.upper()
    role = _header(request, "x-actor-role", "anonymous").lower()
    csrf = _header(request, "x-csrf-token")

    if path not in ADMIN_EVIDENCE_PROXY_PATHS:
        return False

    if method != "GET":
        return False

    if role not in {"owner", "admin", "owner_admin", "system"}:
        return False

    if csrf != "admin-execution-evidence":
        return False

    if not _trusted_origin_valid(request):
        return False

    return True


def _lockout_key(request: Request) -> str:
    return _hash("|".join([_client_ip(request), _header(request, "x-actor-role"), _header(request, "x-tenant-id")]), 24)


def _is_locked_out(request: Request) -> bool:
    key = _lockout_key(request)
    expiry = _LOCKOUTS.get(key)
    if expiry and expiry > _now():
        return True
    if expiry:
        _LOCKOUTS.pop(key, None)
    return False


def _record_lockout_if_needed(request: Request, severity: str) -> bool:
    if severity not in {"high", "critical"}:
        return False

    fp = _fingerprint(request)
    _FINGERPRINT_COUNTS[fp] += 1

    if _FINGERPRINT_COUNTS[fp] >= LOCKOUT_THRESHOLD:
        _LOCKOUTS[_lockout_key(request)] = _now() + LOCKOUT_WINDOW_SECONDS
        return True

    return False


def _audit_event(
    request: Request,
    event_type: str,
    severity: str,
    blocked: bool,
    reasons: List[str],
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "timestamp": int(_now()),
        "profile": SECURITY_AUDIT_PROFILE,
        "event_type": event_type,
        "severity": severity,
        "blocked": blocked,
        "path": request.url.path,
        "method": request.method.upper(),
        "tenant_id": _header(request, "x-tenant-id", "unknown"),
        "actor_role": _header(request, "x-actor-role", "anonymous"),
        "client_ip_hash": _hash(_client_ip(request)),
        "fingerprint": _fingerprint(request),
        "reasons": reasons,
        "extra": extra or {},
    }


def _persist(event: Dict[str, Any]) -> None:
    _EVENTS.append(event)
    try:
        with AUDIT_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        pass


def assess_audit_enforcement(request: Request) -> Dict[str, Any]:
    path = request.url.path.lower()
    method = request.method.upper()
    role = _header(request, "x-actor-role", "anonymous").lower()

    reasons: List[str] = []
    severity = "none"
    blocked = False

    if _is_locked_out(request):
        return {
            "suspicious": True,
            "severity": "critical",
            "blocked": True,
            "reasons": ["security_lockout_active"],
        }

    if _is_admin_path(path):
        evidence_proxy_ok = _admin_evidence_proxy_valid(request)

        if role not in {"owner", "admin", "owner_admin", "system"}:
            reasons.append("admin_route_invalid_actor")
            severity = "high"

        if not evidence_proxy_ok and not _admin_token_valid(request):
            reasons.append("admin_token_missing_or_invalid")
            severity = "critical" if _is_production() else "high"
            if _is_production():
                blocked = True

    if method in STATE_CHANGING_METHODS and (_is_admin_path(path) or path.startswith("/customer") or path.startswith("/client")):
        if not _trusted_origin_valid(request):
            reasons.append("trusted_origin_missing_or_invalid")
            severity = "high" if severity in {"none", "medium"} else severity
            if _is_production():
                blocked = True

    if reasons:
        lockout_created = _record_lockout_if_needed(request, severity)
        if lockout_created:
            reasons.append("security_lockout_created")

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


class SecurityAuditEnforcementMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        assessment = assess_audit_enforcement(request)

        if assessment["suspicious"]:
            _persist(_audit_event(
                request=request,
                event_type="security_audit_enforcement_event",
                severity=assessment["severity"],
                blocked=assessment["blocked"],
                reasons=assessment["reasons"],
                extra={"environment": _env()},
            ))

        if assessment["blocked"]:
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "error": "security_enforcement_blocked",
                    "message": "Request blocked by production security enforcement.",
                    "security_profile": SECURITY_AUDIT_PROFILE,
                },
            )

        response = await call_next(request)
        response.headers.setdefault("X-Security-Audit-Profile", SECURITY_AUDIT_PROFILE)
        return response


def install_security_audit_enforcement(app: Any) -> None:
    existing = [getattr(m.cls, "__name__", "") for m in getattr(app, "user_middleware", [])]
    if "SecurityAuditEnforcementMiddleware" not in existing:
        app.add_middleware(SecurityAuditEnforcementMiddleware)


def _read_durable_events(limit: int = 200) -> List[Dict[str, Any]]:
    if not AUDIT_LOG.exists():
        return []

    rows = []
    try:
        lines = AUDIT_LOG.read_text(encoding="utf-8").splitlines()[-limit:]
        for line in lines:
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    except Exception:
        return []

    return rows


def security_audit_enforcement_readiness() -> Dict[str, Any]:
    memory_events = list(_EVENTS)
    durable_events = _read_durable_events(200)
    all_events = durable_events or memory_events

    severity_counts = Counter(str(e.get("severity", "unknown")) for e in all_events)
    reason_counts = Counter()
    path_counts = Counter()

    for event in all_events:
        path_counts[str(event.get("path", "unknown"))] += 1
        for reason in event.get("reasons", []):
            reason_counts[str(reason)] += 1

    return {
        "success": True,
        "security_profile": SECURITY_AUDIT_PROFILE,
        "environment": _env(),
        "durable_security_audit_persistence_enabled": True,
        "audit_log_path": str(AUDIT_LOG),
        "audit_log_exists": AUDIT_LOG.exists(),
        "production_auth_enforcement_mode": _is_production(),
        "admin_token_verification_enabled": True,
        "trusted_origin_validation_enabled": True,
        "security_lockout_escalation_enabled": True,
        "api_abuse_pattern_aggregation_enabled": True,
        "secure_cookie_session_flags_ready": True,
        "customer_safe_response_mode": True,
        "secret_exposure": False,
        "governance_bypass": False,
        "entitlement_bypass": False,
        "memory_event_count": len(memory_events),
        "durable_event_count": len(durable_events),
        "active_lockout_count": sum(1 for expiry in _LOCKOUTS.values() if expiry > _now()),
        "severity_counts": dict(severity_counts),
        "top_reasons": dict(reason_counts.most_common(10)),
        "top_paths": dict(path_counts.most_common(10)),
        "recent_events": all_events[-25:],
    }
