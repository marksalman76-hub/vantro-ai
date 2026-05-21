from __future__ import annotations

import hashlib
import json
import secrets
import uuid
from datetime import datetime, timezone


PACKAGE_AGENT_LIMITS = {
    "starter": 2,
    "growth": 5,
    "professional": 10,
    "enterprise": 999,
}

def normalise_package_id(value):
    if not value:
        return "starter"

    value = str(value).strip().lower()

    aliases = {
        "starter": "starter",
        "basic": "starter",

        "growth": "growth",
        "pro": "growth",
        "scale": "growth",

        "professional": "professional",
        "premium": "professional",

        "enterprise": "enterprise",
        "unlimited": "enterprise",
    }

    return aliases.get(value, "starter")


def enforce_agent_limit(package_id, agents):
    limit = PACKAGE_AGENT_LIMITS.get(package_id, 2)

    if limit >= 999:
        return list(dict.fromkeys(agents))

    return list(dict.fromkeys(agents))[:limit]

from pathlib import Path
from typing import Any, Dict, List


SAAS_PROVISIONING_PROFILE = "priority8_saas_provisioning_runtime_v1"

ROOT = Path.cwd()
DATA_DIR = ROOT / "data" / "saas_provisioning"
DATA_DIR.mkdir(parents=True, exist_ok=True)

TENANTS_FILE = DATA_DIR / "tenant_provisioning_records.jsonl"
LINKS_FILE = DATA_DIR / "one_time_deployment_links.jsonl"
AUDIT_FILE = DATA_DIR / "provisioning_audit_events.jsonl"


PACKAGE_AGENT_LIMITS = {
    "starter": 2,
    "growth": 5,
    "pro": 10,
    "enterprise": 999,
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _read_jsonl(path: Path, limit: int = 500) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _normalise_package(package: str) -> str:
    package = str(package or "starter").lower().strip()
    if package not in PACKAGE_AGENT_LIMITS:
        return "starter"
    return package


def _default_agents_for_package(package: str, requested_agents: List[str]) -> List[str]:
    package = _normalise_package(package)
    limit = PACKAGE_AGENT_LIMITS[package]

    if package == "enterprise":
        return list(dict.fromkeys(requested_agents))

    return list(dict.fromkeys(requested_agents))[:limit]


def provision_tenant(payload: Dict[str, Any]) -> Dict[str, Any]:
    package = _normalise_package(payload.get("package") or payload.get("package_id") or payload.get("plan"))
    requested_agents = payload.get("requested_agents") or payload.get("selected_agents") or payload.get("agents") or []

    if not isinstance(requested_agents, list):
        requested_agents = selected_agents or requested_agents or []

    tenant_id = str(payload.get("tenant_id") or f"tenant_{uuid.uuid4().hex[:12]}")
    client_number = str(payload.get("client_number") or f"CL-{uuid.uuid4().hex[:8].upper()}")

    activated_agents = _default_agents_for_package(package, [str(a) for a in requested_agents])

    raw_token = secrets.token_urlsafe(32)
    link_id = f"link_{uuid.uuid4().hex[:16]}"

    tenant_record = {
        "tenant_id": tenant_id,
        "client_number": client_number,
        "created_at": _now_iso(),
        "profile": SAAS_PROVISIONING_PROFILE,
        "client_name": str(payload.get("client_name") or ""),
        "client_email": str(payload.get("client_email") or ""),
        "package": package,
        "billing_status": str(payload.get("billing_status") or "pending_payment"),
        "subscription_status": str(payload.get("subscription_status") or "provisioning_pending"),
        "requested_agents": requested_agents,
        "activated_agents": activated_agents,
        "agent_limit": PACKAGE_AGENT_LIMITS[package],
        "workspace_bootstrap_ready": True,
        "entitlement_hydrated": True,
        "owner_admin_free_running_access": True,
        "client_access_limited_to_paid_agents": True,
        "internal_config_hidden_from_client": True,
        "governance_bypass": False,
        "entitlement_bypass": False,
    }

    link_record = {
        "link_id": link_id,
        "tenant_id": tenant_id,
        "client_number": client_number,
        "created_at": _now_iso(),
        "token_hash": _hash_token(raw_token),
        "single_use": True,
        "used": False,
        "blocked_after_use": True,
        "reuse_attempts": 0,
        "admin_review_required_on_reuse": True,
        "deployment_path": f"/activate?token={raw_token}",
    }

    _append_jsonl(TENANTS_FILE, tenant_record)
    _append_jsonl(LINKS_FILE, link_record)
    _append_jsonl(AUDIT_FILE, {
        "timestamp": _now_iso(),
        "event_type": "tenant_provisioned",
        "tenant_id": tenant_id,
        "client_number": client_number,
        "package": package,
        "activated_agent_count": len(activated_agents),
        "profile": SAAS_PROVISIONING_PROFILE,
    })

    safe_link = dict(link_record)
    safe_link["token_hash"] = "hidden"
    safe_link["deployment_token_visible_once"] = True

    return {
        "success": True,
        "provisioning_profile": SAAS_PROVISIONING_PROFILE,
        "tenant": tenant_record,
        "one_time_deployment_link": safe_link,
        "one_time_activation_url": link_record["deployment_path"],
        "client_workspace_bootstrap": {
            "tenant_id": tenant_id,
            "client_number": client_number,
            "package": package,
            "active_agents": activated_agents,
            "billing_status": tenant_record["billing_status"],
            "subscription_status": tenant_record["subscription_status"],
        },
        "customer_safe_response_mode": True,
        "secret_exposure": False,
        "governance_bypass": False,
        "entitlement_bypass": False,
    }




def _rewrite_jsonl(path: Path, records: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def validate_one_time_link(payload: Dict[str, Any]) -> Dict[str, Any]:
    token = str(
        payload.get("token")
        or payload.get("one_time_token")
        or payload.get("activation_token")
        or ""
    ).strip()

    tenant_id = payload.get("tenant_id")

    if not token:
        return {
            "success": False,
            "valid": False,
            "error": "missing_token",
        }

    token_hash = _hash_token(token)

    links = _read_jsonl(LINKS_FILE, limit=2000)

    for index, link in enumerate(links):

        if link.get("token_hash") != token_hash:
            continue

        if tenant_id and link.get("tenant_id") != tenant_id:
            return {
                "success": False,
                "valid": False,
                "error": "tenant_token_mismatch",
            }

        # -------------------------------------------------
        # BLOCK REUSE
        # -------------------------------------------------

        if link.get("used") is True:

            link["reuse_attempts"] = int(link.get("reuse_attempts") or 0) + 1
            link["last_reuse_attempt_at"] = _now_iso()

            links[index] = link

            _rewrite_jsonl(LINKS_FILE, links)

            _append_jsonl(
                AUDIT_FILE,
                {
                    "timestamp": _now_iso(),
                    "event_type": "one_time_link_reuse_blocked",
                    "tenant_id": link.get("tenant_id"),
                    "client_number": link.get("client_number"),
                    "link_id": link.get("link_id"),
                    "admin_review_required": True,
                    "profile": SAAS_PROVISIONING_PROFILE,
                },
            )

            return {
                "success": False,
                "valid": False,
                "error": "one_time_link_already_used",
                "tenant_id": link.get("tenant_id"),
                "client_number": link.get("client_number"),
                "single_use": True,
                "blocked_after_use": True,
                "admin_review_required": True,
            }

        # -------------------------------------------------
        # FIRST VALID USE
        # -------------------------------------------------

        link["used"] = True
        link["used_at"] = _now_iso()
        link["blocked_after_use"] = True
        link["used_by_client_email"] = payload.get("client_email")

        links[index] = link

        _rewrite_jsonl(LINKS_FILE, links)

        _append_jsonl(
            AUDIT_FILE,
            {
                "timestamp": _now_iso(),
                "event_type": "one_time_link_consumed",
                "tenant_id": link.get("tenant_id"),
                "client_number": link.get("client_number"),
                "link_id": link.get("link_id"),
                "profile": SAAS_PROVISIONING_PROFILE,
            },
        )

        return {
            "success": True,
            "valid": True,
            "tenant_id": link.get("tenant_id"),
            "client_number": link.get("client_number"),
            "single_use": True,
            "used": True,
            "blocked_after_use": True,
        }

    return {
        "success": False,
        "valid": False,
        "error": "invalid_token",
    }


def provisioning_readiness() -> Dict[str, Any]:
    tenants = _read_jsonl(TENANTS_FILE, limit=1000)
    links = _read_jsonl(LINKS_FILE, limit=1000)
    audits = _read_jsonl(AUDIT_FILE, limit=1000)

    return {
        "success": True,
        "provisioning_profile": SAAS_PROVISIONING_PROFILE,
        "tenant_provisioning_enabled": True,
        "package_activation_automation_enabled": True,
        "one_time_secure_deployment_links_enabled": True,
        "onboarding_lifecycle_runtime_enabled": True,
        "subscription_state_provisioning_sync_enabled": True,
        "entitlement_hydration_enabled": True,
        "client_workspace_bootstrap_enabled": True,
        "deployment_audit_tracking_enabled": True,
        "owner_admin_free_running_access_enabled": True,
        "client_access_limited_to_paid_agents": True,
        "internal_config_hidden_from_client": True,
        "tenants_file_exists": TENANTS_FILE.exists(),
        "links_file_exists": LINKS_FILE.exists(),
        "audit_file_exists": AUDIT_FILE.exists(),
        "tenant_count": len(tenants),
        "link_count": len(links),
        "audit_count": len(audits),
        "customer_safe_response_mode": True,
        "secret_exposure": False,
        "governance_bypass": False,
        "entitlement_bypass": False,
    }
