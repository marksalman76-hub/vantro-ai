"""
Rate-shaping middleware.

Default mode is observe-only:
- Does not block requests unless RATE_SHAPING_MODE=enforce.
- Preserves owner/admin operational access.
- Adds safe response headers for visibility.
- Uses in-memory counters as a lightweight first activation layer.
"""

from __future__ import annotations

import os
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from backend.app.core.rate_shaping_policy import get_policy_for_path, should_owner_admin_bypass


class RateShapingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._requests: Dict[Tuple[str, str], Deque[float]] = defaultdict(deque)

    def _mode(self) -> str:
        return (os.getenv("RATE_SHAPING_MODE") or "observe").strip().lower()

    def _is_enabled(self) -> bool:
        return (os.getenv("RATE_SHAPING_ENABLED") or "true").strip().lower() in {"1", "true", "yes", "on"}

    def _client_key(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for", "")
        if forwarded:
            return forwarded.split(",")[0].strip() or "unknown"
        if request.client and request.client.host:
            return request.client.host
        return "unknown"

    def _actor_role(self, request: Request) -> str:
        return (
            request.headers.get("x-actor-role")
            or request.headers.get("x-admin-role")
            or request.headers.get("x-owner-role")
            or ""
        ).lower()

    def _is_owner_admin(self, request: Request) -> bool:
        role = self._actor_role(request)
        if role in {"owner", "admin", "owner_admin", "super_admin"}:
            return True
        if request.headers.get("x-admin-token") or request.headers.get("authorization"):
            return True
        return False

    def _allow_and_record(self, key: Tuple[str, str], limit: int, burst: int) -> Tuple[bool, int]:
        now = time.time()
        window_start = now - 60
        bucket = self._requests[key]

        while bucket and bucket[0] < window_start:
            bucket.popleft()

        current = len(bucket)
        allowed = current < max(limit, burst)
        if allowed:
            bucket.append(now)

        remaining = max(0, max(limit, burst) - len(bucket))
        return allowed, remaining

    async def dispatch(self, request: Request, call_next):
        if not self._is_enabled():
            response = await call_next(request)
            response.headers["x-rate-shaping"] = "disabled"
            return response

        path = request.url.path
        policy = get_policy_for_path(path)
        route_group = policy.route_group

        owner_admin_bypass = should_owner_admin_bypass(path) and self._is_owner_admin(request)
        key = (route_group, self._client_key(request))

        allowed, remaining = self._allow_and_record(
            key,
            policy.limit_per_minute,
            policy.burst_limit,
        )

        mode = self._mode()

        if not allowed and mode == "enforce" and not owner_admin_bypass:
            return JSONResponse(
                {
                    "success": False,
                    "error": "rate_limit_exceeded",
                    "route_group": route_group,
                    "customer_safe": True,
                },
                status_code=429,
                headers={
                    "x-rate-shaping": "enforced",
                    "x-rate-shaping-route-group": route_group,
                    "x-rate-shaping-remaining": str(remaining),
                },
            )

        response: Response = await call_next(request)
        response.headers["x-rate-shaping"] = "observe" if mode != "enforce" else "enforce"
        response.headers["x-rate-shaping-route-group"] = route_group
        response.headers["x-rate-shaping-remaining"] = str(remaining)
        response.headers["x-rate-shaping-owner-admin-bypass"] = str(bool(owner_admin_bypass)).lower()
        return response


def rate_shaping_middleware_default_mode() -> str:
    return os.getenv("RATE_SHAPING_MODE") or "observe"


def rate_shaping_middleware_changes_live_runtime() -> bool:
    return True


def rate_shaping_middleware_blocks_by_default() -> bool:
    return False
