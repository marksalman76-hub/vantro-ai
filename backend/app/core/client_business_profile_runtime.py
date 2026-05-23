from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict

from backend.app.core.postgres_account_runtime import get_connection, get_session_account


PROFILE_FIELDS = [
    "business_niche",
    "products_services",
    "target_audience",
    "competitors",
    "offers",
    "brand_voice",
    "goals",
    "region",
    "currency",
    "notes",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalise_profile(payload: Dict[str, Any]) -> Dict[str, str]:
    profile: Dict[str, str] = {}
    for field in PROFILE_FIELDS:
        value = payload.get(field)
        profile[field] = str(value or "").strip()[:4000]
    return profile


def ensure_client_business_profile_table() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS client_business_profiles (
                tenant_id TEXT PRIMARY KEY,
                profile_json TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL,
                updated_at TIMESTAMPTZ NOT NULL
            )
            """)
        conn.commit()


def get_client_business_profile(session_token: str) -> Dict[str, Any]:
    session = get_session_account(session_token)

    if not session.get("success"):
        return {"success": False, "error": session.get("error") or "invalid_session"}

    account = session.get("account") or {}
    tenant_id = str(account.get("tenant_id") or "").strip()

    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    ensure_client_business_profile_table()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT profile_json, created_at, updated_at
            FROM client_business_profiles
            WHERE tenant_id = %s
            """, (tenant_id,))
            row = cur.fetchone()

    if not row:
        return {
            "success": True,
            "tenant_id": tenant_id,
            "account": account,
            "profile": {field: "" for field in PROFILE_FIELDS},
            "profile_saved": False,
        }

    try:
        profile = json.loads(row[0] or "{}")
    except Exception:
        profile = {}

    profile = {field: str(profile.get(field) or "") for field in PROFILE_FIELDS}

    return {
        "success": True,
        "tenant_id": tenant_id,
        "account": account,
        "profile": profile,
        "profile_saved": True,
        "created_at": row[1].isoformat() if row[1] else None,
        "updated_at": row[2].isoformat() if row[2] else None,
    }


def save_client_business_profile(session_token: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    session = get_session_account(session_token)

    if not session.get("success"):
        return {"success": False, "error": session.get("error") or "invalid_session"}

    account = session.get("account") or {}
    tenant_id = str(account.get("tenant_id") or "").strip()

    if not tenant_id:
        return {"success": False, "error": "tenant_id_required"}

    profile = _normalise_profile(payload)
    ensure_client_business_profile_table()

    now = _now_iso()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO client_business_profiles (
                tenant_id,
                profile_json,
                created_at,
                updated_at
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (tenant_id)
            DO UPDATE SET
                profile_json = EXCLUDED.profile_json,
                updated_at = EXCLUDED.updated_at
            RETURNING tenant_id, profile_json, created_at, updated_at
            """, (
                tenant_id,
                json.dumps(profile),
                now,
                now,
            ))
            row = cur.fetchone()
        conn.commit()

    return {
        "success": True,
        "tenant_id": row[0],
        "account": account,
        "profile": json.loads(row[1] or "{}"),
        "profile_saved": True,
        "created_at": row[2].isoformat() if row[2] else None,
        "updated_at": row[3].isoformat() if row[3] else None,
        "customer_safe_response_mode": True,
    }
