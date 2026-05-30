"""
Safe rate-shaping policy foundation.

This module defines route-aware request classification and recommended limits.
It does not enforce throttling by itself. Enforcement should be wired only after
verification so owner/admin access, governance, and customer execution remain safe.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class RatePolicy:
    route_group: str
    limit_per_minute: int
    burst_limit: int
    owner_admin_bypass: bool
    client_safe: bool
    notes: str


POLICIES: Dict[str, RatePolicy] = {
    "health": RatePolicy(
        route_group="health",
        limit_per_minute=600,
        burst_limit=100,
        owner_admin_bypass=False,
        client_safe=True,
        notes="Cheap health checks. Keep separate from deep readiness checks.",
    ),
    "readiness": RatePolicy(
        route_group="readiness",
        limit_per_minute=120,
        burst_limit=30,
        owner_admin_bypass=True,
        client_safe=False,
        notes="Deeper readiness/admin checks should be protected from public flooding.",
    ),
    "client_execution": RatePolicy(
        route_group="client_execution",
        limit_per_minute=60,
        burst_limit=15,
        owner_admin_bypass=False,
        client_safe=True,
        notes="Client-facing execution should be shaped but not blocked unexpectedly.",
    ),
    "admin_execution": RatePolicy(
        route_group="admin_execution",
        limit_per_minute=300,
        burst_limit=75,
        owner_admin_bypass=True,
        client_safe=False,
        notes="Owner/admin operational usage may bypass client limits but remains audited.",
    ),
    "provider_execution": RatePolicy(
        route_group="provider_execution",
        limit_per_minute=30,
        burst_limit=10,
        owner_admin_bypass=True,
        client_safe=False,
        notes="Provider/live actions require governance and should be queue-isolated.",
    ),
    "auth": RatePolicy(
        route_group="auth",
        limit_per_minute=20,
        burst_limit=5,
        owner_admin_bypass=False,
        client_safe=True,
        notes="Login/session routes should be strongly protected.",
    ),
    "public": RatePolicy(
        route_group="public",
        limit_per_minute=120,
        burst_limit=30,
        owner_admin_bypass=False,
        client_safe=True,
        notes="Default public API protection.",
    ),
}


def classify_route(path: str) -> str:
    normalized = (path or "/").lower()

    if normalized == "/health" or normalized.endswith("/health"):
        return "health"

    if "readiness" in normalized or normalized.endswith("/ready"):
        return "readiness"

    if "admin" in normalized:
        if "provider" in normalized or "live-execution" in normalized:
            return "provider_execution"
        return "admin_execution"

    if "login" in normalized or "activate" in normalized or "session" in normalized:
        return "auth"

    if "run-agent" in normalized or "delegated-workforce" in normalized or "execution" in normalized:
        return "client_execution"

    return "public"


def get_policy_for_path(path: str) -> RatePolicy:
    return POLICIES[classify_route(path)]


def should_owner_admin_bypass(path: str) -> bool:
    return get_policy_for_path(path).owner_admin_bypass


def export_rate_policy_snapshot() -> dict:
    return {
        name: {
            "route_group": policy.route_group,
            "limit_per_minute": policy.limit_per_minute,
            "burst_limit": policy.burst_limit,
            "owner_admin_bypass": policy.owner_admin_bypass,
            "client_safe": policy.client_safe,
            "notes": policy.notes,
        }
        for name, policy in POLICIES.items()
    }
