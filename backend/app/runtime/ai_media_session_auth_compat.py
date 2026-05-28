"""
Priority 1 AI media session/auth compatibility runtime.

Purpose:
- Allows owner/admin execution for governed AI media generation routes.
- Preserves priority5_session_auth_hardening_v1.
- Does not allow public/client execution.
- Does not expose internal prompts, secrets, or provider credentials.
"""

from __future__ import annotations

import os
from typing import Any, Dict


AI_MEDIA_ADMIN_COMPAT_PATHS = {
    "/admin/ai-media-pipeline/run",
    "/admin/provider-action-readiness",
    "/admin/provider-action-readiness/evaluate",
}


def _split_csv(value: str) -> set[str]:
    return {item.strip().rstrip("/") for item in value.split(",") if item.strip()}


def _configured_admin_tokens() -> set[str]:
    names = (
        "ADMIN_PLATFORM_TOKEN",
        "ADMIN_AUTH_SECRET",
        "OWNER_ADMIN_TOKEN",
        "ADMIN_TOKEN",
    )
    values = set()
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            values.add(value)
    return values


def _allowed_origins() -> set[str]:
    origins = set()
    for name in (
        "FRONTEND_URL",
        "NEXT_PUBLIC_FRONTEND_URL",
        "CORS_ALLOWED_ORIGINS",
        "ALLOWED_ORIGINS",
    ):
        value = os.getenv(name, "").strip()
        if value:
            origins |= _split_csv(value)
    return {origin.rstrip("/") for origin in origins if origin}


def validate_ai_media_admin_session_compatibility(request: Any) -> Dict[str, Any]:
    path = getattr(getattr(request, "url", None), "path", "") or ""
    method = (getattr(request, "method", "") or "").upper()
    headers = getattr(request, "headers", {}) or {}

    if path not in AI_MEDIA_ADMIN_COMPAT_PATHS:
        return {
            "allowed": False,
            "success": False,
            "error": "auth_security_policy_blocked",
            "message": "Route is not registered for AI media admin session compatibility.",
            "security_profile": "priority5_session_auth_hardening_v1",
        }

    allowed_methods = {
        "/admin/ai-media-pipeline/run": {"POST", "OPTIONS"},
        "/admin/provider-action-readiness": {"GET", "OPTIONS"},
        "/admin/provider-action-readiness/evaluate": {"POST", "OPTIONS"},
    }

    if method not in allowed_methods.get(path, set()):
        return {
            "allowed": False,
            "success": False,
            "error": "auth_security_policy_blocked",
            "message": "Unsupported method for governed AI media admin execution.",
            "security_profile": "priority5_session_auth_hardening_v1",
        }

    actor_role = (
        headers.get("x-actor-role")
        or headers.get("X-Actor-Role")
        or headers.get("x-user-role")
        or headers.get("X-User-Role")
        or ""
    ).strip().lower()

    if actor_role not in {"owner", "admin", "owner_admin", "platform_admin", "super_admin"}:
        return {
            "allowed": False,
            "success": False,
            "error": "auth_security_policy_blocked",
            "message": "AI media generation requires owner/admin session context.",
            "security_profile": "priority5_session_auth_hardening_v1",
        }

    auth_header = (
        headers.get("authorization")
        or headers.get("Authorization")
        or ""
    ).strip()

    bearer_token = ""
    if auth_header.lower().startswith("bearer "):
        bearer_token = auth_header.split(" ", 1)[1].strip()

    explicit_admin_token = (
        headers.get("x-admin-token")
        or headers.get("X-Admin-Token")
        or headers.get("x-platform-admin-token")
        or headers.get("X-Platform-Admin-Token")
        or ""
    ).strip()

    configured_tokens = _configured_admin_tokens()
    supplied_tokens = {token for token in (bearer_token, explicit_admin_token) if token}

    if configured_tokens and not (configured_tokens & supplied_tokens):
        return {
            "allowed": False,
            "success": False,
            "error": "auth_security_policy_blocked",
            "message": "Valid owner/admin token required for AI media generation.",
            "security_profile": "priority5_session_auth_hardening_v1",
        }

    origin = (
        headers.get("origin")
        or headers.get("Origin")
        or ""
    ).strip().rstrip("/")

    allowed_origins = _allowed_origins()
    if origin and allowed_origins and origin not in allowed_origins:
        return {
            "allowed": False,
            "success": False,
            "error": "auth_security_policy_blocked",
            "message": "Origin is not allowed for governed AI media generation.",
            "security_profile": "priority5_session_auth_hardening_v1",
        }

    return {
        "allowed": True,
        "success": True,
        "security_profile": "priority5_session_auth_hardening_v1",
        "compatibility_profile": "priority1_ai_media_admin_session_auth_compat_v1",
        "governance_preserved": True,
        "owner_admin_only": True,
        "client_public_access_blocked": True,
    }
