from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from backend.app.runtime.canonical_entitlement_activation_runtime import activate_entitlement_once


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
ACCOUNT_STORE = DATA_DIR / "tenant_client_accounts.json"

PBKDF2_ITERATIONS = 240_000
INVITE_EXPIRY_HOURS = 72
SESSION_EXPIRY_HOURS = 8


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _load_store() -> Dict[str, Any]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not ACCOUNT_STORE.exists():
        return {
            "invites": {},
            "accounts": {},
            "sessions": {},
            "security_events": [],
        }

    try:
        data = json.loads(ACCOUNT_STORE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        data = {}

    data.setdefault("invites", {})
    data.setdefault("accounts", {})
    data.setdefault("sessions", {})
    data.setdefault("security_events", [])
    return data


def _save_store(data: Dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ACCOUNT_STORE.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _hash_password(password: str, salt: Optional[str] = None) -> Dict[str, Any]:
    if not salt:
        salt = secrets.token_urlsafe(32)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    )

    return {
        "algorithm": "pbkdf2_sha256",
        "iterations": PBKDF2_ITERATIONS,
        "salt": salt,
        "hash": base64.b64encode(digest).decode("utf-8"),
    }


def _verify_password(password: str, password_record: Dict[str, Any]) -> bool:
    if not password_record:
        return False

    if password_record.get("algorithm") != "pbkdf2_sha256":
        return False

    expected = password_record.get("hash", "")
    salt = password_record.get("salt", "")
    iterations = int(password_record.get("iterations", PBKDF2_ITERATIONS))

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )

    actual = base64.b64encode(digest).decode("utf-8")
    return hmac.compare_digest(actual, expected)


def _safe_account(account: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "tenant_id": account.get("tenant_id"),
        "email": account.get("email"),
        "company_name": account.get("company_name"),
        "package": account.get("package"),
        "active_agents": account.get("active_agents", []),
        "status": account.get("status"),
        "created_at": account.get("created_at"),
        "activated_at": account.get("activated_at"),
    }


def _log_security_event(data: Dict[str, Any], event_type: str, details: Dict[str, Any]) -> None:
    data.setdefault("security_events", []).append(
        {
            "event_type": event_type,
            "details": details,
            "created_at": _iso(_now()),
        }
    )


def create_client_activation_invite(payload: Dict[str, Any]) -> Dict[str, Any]:
    data = _load_store()

    tenant_id = str(payload.get("tenant_id") or "").strip()
    email = str(payload.get("email") or "").strip().lower()
    company_name = str(payload.get("company_name") or "").strip()
    package = str(payload.get("package") or "trial").strip()
    active_agents = payload.get("active_agents") or []

    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    if not email or "@" not in email:
        return {"success": False, "error": "valid_email_required"}

    token = secrets.token_urlsafe(48)
    expires_at = _now() + timedelta(hours=INVITE_EXPIRY_HOURS)

    data["invites"][token] = {
        "token": token,
        "tenant_id": tenant_id,
        "email": email,
        "company_name": company_name,
        "package": package,
        "active_agents": active_agents,
        "status": "pending",
        "created_at": _iso(_now()),
        "expires_at": _iso(expires_at),
        "used_at": None,
    }

    _save_store(data)

    return {
        "success": True,
        "tenant_id": tenant_id,
        "email": email,
        "activation_token": token,
        "activation_path": f"/activate?token={token}",
        "expires_at": _iso(expires_at),
        "secret_values_included": False,
    }


def get_invite_status(token: str) -> Dict[str, Any]:
    data = _load_store()
    invite = data["invites"].get(token)

    if not invite:
        return {"success": False, "error": "invite_not_found"}

    expired = datetime.fromisoformat(invite["expires_at"]) < _now()
    used = invite.get("status") == "used"

    return {
        "success": True,
        "tenant_id": invite.get("tenant_id"),
        "email": invite.get("email"),
        "company_name": invite.get("company_name"),
        "package": invite.get("package"),
        "active_agents": invite.get("active_agents", []),
        "status": invite.get("status"),
        "expired": expired,
        "used": used,
    }


def activate_client_account(payload: Dict[str, Any]) -> Dict[str, Any]:
    data = _load_store()

    token = str(payload.get("token") or "").strip()
    password = str(payload.get("password") or "")
    confirm_password = str(payload.get("confirm_password") or "")

    invite = data["invites"].get(token)

    if not invite:
        _log_security_event(data, "invalid_activation_token_attempt", {"token_hint": token[:8]})
        _save_store(data)
        return {"success": False, "error": "invalid_activation_token"}

    if invite.get("status") == "used":
        _log_security_event(
            data,
            "reused_activation_token_blocked",
            {"tenant_id": invite.get("tenant_id"), "email": invite.get("email")},
        )
        _save_store(data)
        return {"success": False, "error": "activation_link_already_used"}

    if datetime.fromisoformat(invite["expires_at"]) < _now():
        _log_security_event(
            data,
            "expired_activation_token_blocked",
            {"tenant_id": invite.get("tenant_id"), "email": invite.get("email")},
        )
        _save_store(data)
        return {"success": False, "error": "activation_link_expired"}

    if len(password) < 10:
        return {"success": False, "error": "password_minimum_10_characters"}

    if password != confirm_password:
        return {"success": False, "error": "passwords_do_not_match"}

    tenant_id = invite["tenant_id"]
    email = invite["email"]

    account = {
        "tenant_id": tenant_id,
        "email": email,
        "company_name": invite.get("company_name"),
        "package": invite.get("package"),
        "active_agents": invite.get("active_agents", []),
        "status": "active",
        "password": _hash_password(password),
        "created_at": invite.get("created_at"),
        "activated_at": _iso(_now()),
    }

    data["accounts"][email] = account
    invite["status"] = "used"
    invite["used_at"] = _iso(_now())

    _save_store(data)

    entitlement_activation = activate_entitlement_once(
        tenant_id=tenant_id,
        package=invite.get("package"),
        selected_agents=invite.get("active_agents", []),
        actor_role="system",
        source="tenant_account_runtime_compat",
    )

    return {
        "success": True,
        "account": _safe_account(account),
        "account_store_role": "compatibility_cache",
        "canonical_entitlement_activation": entitlement_activation,
    }


def login_client_account(payload: Dict[str, Any]) -> Dict[str, Any]:
    data = _load_store()

    email = str(payload.get("email") or "").strip().lower()
    password = str(payload.get("password") or "")

    account = data["accounts"].get(email)

    if not account or account.get("status") != "active":
        _log_security_event(data, "failed_login_unknown_or_inactive_account", {"email": email})
        _save_store(data)
        return {"success": False, "error": "invalid_login"}

    if not _verify_password(password, account.get("password", {})):
        _log_security_event(data, "failed_login_invalid_password", {"email": email})
        _save_store(data)
        return {"success": False, "error": "invalid_login"}

    session_token = secrets.token_urlsafe(48)
    expires_at = _now() + timedelta(hours=SESSION_EXPIRY_HOURS)

    data["sessions"][session_token] = {
        "session_token": session_token,
        "email": email,
        "tenant_id": account.get("tenant_id"),
        "created_at": _iso(_now()),
        "expires_at": _iso(expires_at),
        "status": "active",
    }

    _save_store(data)

    return {
        "success": True,
        "session_token": session_token,
        "expires_at": _iso(expires_at),
        "account": _safe_account(account),
    }


def get_account_from_session(session_token: str) -> Dict[str, Any]:
    data = _load_store()
    session = data["sessions"].get(session_token)

    if not session or session.get("status") != "active":
        return {"success": False, "error": "invalid_session"}

    if datetime.fromisoformat(session["expires_at"]) < _now():
        session["status"] = "expired"
        _save_store(data)
        return {"success": False, "error": "session_expired"}

    account = data["accounts"].get(session["email"])

    if not account:
        return {"success": False, "error": "account_not_found"}

    return {
        "success": True,
        "account": _safe_account(account),
    }


def logout_session(session_token: str) -> Dict[str, Any]:
    data = _load_store()

    if session_token in data["sessions"]:
        data["sessions"][session_token]["status"] = "logged_out"
        data["sessions"][session_token]["logged_out_at"] = _iso(_now())
        _save_store(data)

    return {"success": True}


def get_tenant_account_security_events(limit: int = 25) -> Dict[str, Any]:
    data = _load_store()
    events = list(reversed(data.get("security_events", [])))[:limit]
    return {"success": True, "events": events}
