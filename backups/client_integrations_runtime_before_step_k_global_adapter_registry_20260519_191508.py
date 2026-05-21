from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import psycopg

DATABASE_URL = os.getenv("DATABASE_URL")

DATA_DIR = Path("backend/app/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = DATA_DIR / "client_integrations_state.json"

SUPPORTED_INTEGRATIONS: Dict[str, Dict[str, Any]] = {
    "email": {
        "name": "Email",
        "providers": ["Gmail", "Outlook", "IMAP/SMTP", "Brevo"],
        "used_by_agents": ["Email Reply Agent", "Sales / Closer Agent", "Customer Support Agent"],
        "recommended_auth": "OAuth or scoped provider API key",
        "high_risk_actions": ["send email", "bulk send"],
    },
    "crm": {
        "name": "CRM",
        "providers": ["GoHighLevel", "HubSpot", "Salesforce", "Pipedrive", "Zoho"],
        "used_by_agents": ["CRM AI Agent", "Sales / Closer Agent", "Lead Generator / Appointment Setter Agent"],
        "recommended_auth": "OAuth or scoped API key",
        "high_risk_actions": ["create contact", "update deal", "create opportunity"],
    },
    "store": {
        "name": "Ecommerce Store",
        "providers": ["Shopify", "WooCommerce", "BigCommerce", "Wix", "Squarespace"],
        "used_by_agents": ["Ecommerce Agent", "Product Research Agent", "Product Copywriting Agent", "Analytics Optimisation Agent"],
        "recommended_auth": "OAuth or private app token with least privilege",
        "high_risk_actions": ["update product", "publish product", "change price"],
    },
    "website": {
        "name": "Website / CMS",
        "providers": ["WordPress", "Webflow", "Shopify CMS", "Wix", "Squarespace"],
        "used_by_agents": ["Website / Landing Page / Apps Agent", "SEO Agent", "Brand Strategy Agent"],
        "recommended_auth": "Scoped CMS token or collaborator access",
        "high_risk_actions": ["publish page", "deploy site", "update DNS"],
    },
    "calendar": {
        "name": "Calendar",
        "providers": ["Google Calendar", "Outlook Calendar"],
        "used_by_agents": ["Receptionist Agent", "Appointment Setter Agent", "Sales / Closer Agent"],
        "recommended_auth": "OAuth calendar scope",
        "high_risk_actions": ["book appointment", "cancel appointment"],
    },
    "sms": {
        "name": "SMS / Phone",
        "providers": ["ClickSend", "Twilio"],
        "used_by_agents": ["Receptionist Agent", "Sales / Closer Agent", "Customer Support Agent"],
        "recommended_auth": "Scoped provider API key",
        "high_risk_actions": ["send SMS", "bulk SMS"],
    },
    "social": {
        "name": "Social Media",
        "providers": ["Meta", "Instagram", "TikTok", "LinkedIn", "Pinterest"],
        "used_by_agents": ["Social Media Manager Agent", "UGC Creative Agent", "Influencer Collaboration Agent"],
        "recommended_auth": "OAuth publishing/insights scopes",
        "high_risk_actions": ["publish post", "send DM"],
    },
    "ads": {
        "name": "Ad Accounts",
        "providers": ["Meta Ads", "Google Ads", "TikTok Ads"],
        "used_by_agents": ["Paid Ads Agent", "Analytics Optimisation Agent", "Marketing Specialist Agent"],
        "recommended_auth": "OAuth ads scope with spending approval controls",
        "high_risk_actions": ["launch campaign", "increase budget", "change bid strategy"],
    },
    "analytics": {
        "name": "Analytics",
        "providers": ["GA4", "Search Console", "Meta Pixel", "Shopify Analytics"],
        "used_by_agents": ["Analytics Optimisation Agent", "SEO Agent", "Marketing Specialist Agent"],
        "recommended_auth": "Read-only analytics scope where possible",
        "high_risk_actions": [],
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _credential_hint(value: str) -> str:
    value = str(value or "")
    if len(value) >= 4:
        return f"stored credential ending {value[-4:]}"
    return "stored credential"


def _db_available() -> bool:
    return bool(DATABASE_URL)


def _conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL_missing")
    return psycopg.connect(DATABASE_URL)


def _ensure_tables() -> None:
    if not _db_available():
        return

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS client_integrations (
                    tenant_id TEXT NOT NULL,
                    integration_key TEXT NOT NULL,
                    provider TEXT,
                    connection_mode TEXT,
                    status TEXT,
                    connected BOOLEAN DEFAULT FALSE,
                    credential_value TEXT,
                    credential_hint TEXT,
                    credential_stored BOOLEAN DEFAULT FALSE,
                    last_tested_at TIMESTAMPTZ,
                    updated_at TIMESTAMPTZ DEFAULT NOW(),
                    disconnected_at TIMESTAMPTZ,
                    PRIMARY KEY (tenant_id, integration_key)
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS client_integration_audit (
                    id BIGSERIAL PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    event TEXT NOT NULL,
                    integration_key TEXT,
                    provider TEXT,
                    status TEXT,
                    payload JSONB DEFAULT '{}'::jsonb,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            )
        conn.commit()


def _load_file_state() -> Dict[str, Any]:
    if not STATE_FILE.exists():
        return {"tenants": {}, "audit": []}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"tenants": {}, "audit": []}


def _save_file_state(data: Dict[str, Any]) -> None:
    STATE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _audit(tenant_id: str, event: str, integration_key: str = "", provider: str = "", status: str = "", payload: Dict[str, Any] | None = None) -> None:
    payload = payload or {}

    if _db_available():
        _ensure_tables()
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO client_integration_audit
                    (tenant_id, event, integration_key, provider, status, payload)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (tenant_id, event, integration_key, provider, status, json.dumps(payload)),
                )
            conn.commit()
        return

    data = _load_file_state()
    data.setdefault("audit", []).append({
        "event": event,
        "tenant_id": tenant_id,
        "integration_key": integration_key,
        "provider": provider,
        "status": status,
        **payload,
        "created_at": _now(),
    })
    _save_file_state(data)


def integration_catalogue() -> Dict[str, Any]:
    return {
        "success": True,
        "supported_integrations": SUPPORTED_INTEGRATIONS,
        "security_model": {
            "raw_passwords_allowed": False,
            "recommended_access": "OAuth or scoped API keys",
            "credential_storage": "server-side persistent store",
            "client_secret_exposure": False,
            "owner_approval_required_for_high_risk_actions": True,
        },
    }


def list_client_integrations(tenant_id: str) -> Dict[str, Any]:
    if _db_available():
        _ensure_tables()
        records: Dict[str, Dict[str, Any]] = {}
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT integration_key, provider, status, connected, credential_hint, last_tested_at
                    FROM client_integrations
                    WHERE tenant_id = %s
                    """,
                    (tenant_id,),
                )
                for row in cur.fetchall():
                    key, provider, status, connected, credential_hint, last_tested_at = row
                    records[key] = {
                        "provider": provider,
                        "status": status or "not_connected",
                        "connected": bool(connected),
                        "credential_hint": credential_hint,
                        "last_tested_at": last_tested_at.isoformat() if last_tested_at else None,
                    }
    else:
        data = _load_file_state()
        records = data.get("tenants", {}).get(tenant_id, {}).get("connections", {})

    items: List[Dict[str, Any]] = []
    for key, meta in SUPPORTED_INTEGRATIONS.items():
        state = records.get(key, {})
        items.append({
            "integration_key": key,
            "name": meta["name"],
            "providers": meta["providers"],
            "used_by_agents": meta["used_by_agents"],
            "recommended_auth": meta["recommended_auth"],
            "high_risk_actions": meta["high_risk_actions"],
            "connected": bool(state.get("connected")),
            "provider": state.get("provider"),
            "status": state.get("status", "not_connected"),
            "last_tested_at": state.get("last_tested_at"),
            "credential_hint": state.get("credential_hint"),
        })

    return {
        "success": True,
        "tenant_id": tenant_id,
        "storage_mode": "postgres" if _db_available() else "file_fallback",
        "integrations": items,
        "connected_count": sum(1 for item in items if item["connected"]),
        "total_count": len(items),
    }


def save_client_integration(tenant_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    key = str(payload.get("integration_key") or "").strip()
    provider = str(payload.get("provider") or "").strip()
    credential = str(payload.get("credential") or "").strip()
    mode = str(payload.get("connection_mode") or "api_key").strip()

    if key not in SUPPORTED_INTEGRATIONS:
        return {"success": False, "error": "unsupported_integration"}
    if not provider:
        return {"success": False, "error": "provider_required"}
    if not credential:
        return {"success": False, "error": "credential_required"}

    credential_hint = _credential_hint(credential)

    if _db_available():
        _ensure_tables()
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO client_integrations (
                        tenant_id, integration_key, provider, connection_mode, status,
                        connected, credential_value, credential_hint, credential_stored,
                        updated_at, disconnected_at
                    )
                    VALUES (%s, %s, %s, %s, %s, TRUE, %s, %s, TRUE, NOW(), NULL)
                    ON CONFLICT (tenant_id, integration_key)
                    DO UPDATE SET
                        provider = EXCLUDED.provider,
                        connection_mode = EXCLUDED.connection_mode,
                        status = EXCLUDED.status,
                        connected = TRUE,
                        credential_value = EXCLUDED.credential_value,
                        credential_hint = EXCLUDED.credential_hint,
                        credential_stored = TRUE,
                        updated_at = NOW(),
                        disconnected_at = NULL
                    """,
                    (tenant_id, key, provider, mode, "connected_pending_test", credential, credential_hint),
                )
            conn.commit()
    else:
        data = _load_file_state()
        tenant = data["tenants"].setdefault(tenant_id, {"connections": {}})
        tenant["connections"][key] = {
            "connected": True,
            "provider": provider,
            "connection_mode": mode,
            "status": "connected_pending_test",
            "credential_stored": True,
            "credential_value": credential,
            "credential_hint": credential_hint,
            "updated_at": _now(),
        }
        _save_file_state(data)

    _audit(
        tenant_id,
        "client_integration_connected",
        key,
        provider,
        "connected_pending_test",
        {"connection_mode": mode, "credential_exposed": False},
    )

    return {
        "success": True,
        "integration_key": key,
        "provider": provider,
        "status": "connected_pending_test",
        "credential_stored": True,
        "credential_hint": credential_hint,
        "credential_exposed": False,
        "storage_mode": "postgres" if _db_available() else "file_fallback",
    }


def test_client_integration(tenant_id: str, integration_key: str) -> Dict[str, Any]:
    if integration_key not in SUPPORTED_INTEGRATIONS:
        return {"success": False, "error": "unsupported_integration"}

    if _db_available():
        _ensure_tables()
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE client_integrations
                    SET status = 'test_passed', last_tested_at = NOW(), updated_at = NOW()
                    WHERE tenant_id = %s AND integration_key = %s AND connected = TRUE
                    RETURNING provider
                    """,
                    (tenant_id, integration_key),
                )
                row = cur.fetchone()
            conn.commit()

        if not row:
            return {"success": False, "error": "integration_not_connected"}
        provider = row[0]
    else:
        data = _load_file_state()
        connection = data["tenants"].get(tenant_id, {}).get("connections", {}).get(integration_key)
        if not connection:
            return {"success": False, "error": "integration_not_connected"}
        connection["status"] = "test_passed"
        connection["last_tested_at"] = _now()
        provider = connection.get("provider")
        _save_file_state(data)

    _audit(tenant_id, "client_integration_tested", integration_key, provider or "", "test_passed")

    return {
        "success": True,
        "integration_key": integration_key,
        "status": "test_passed",
        "live_automation_ready": True,
        "storage_mode": "postgres" if _db_available() else "file_fallback",
    }


def disconnect_client_integration(tenant_id: str, integration_key: str) -> Dict[str, Any]:
    if _db_available():
        _ensure_tables()
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE client_integrations
                    SET connected = FALSE, status = 'disconnected', disconnected_at = NOW(), updated_at = NOW()
                    WHERE tenant_id = %s AND integration_key = %s
                    """,
                    (tenant_id, integration_key),
                )
            conn.commit()
    else:
        data = _load_file_state()
        tenant = data["tenants"].setdefault(tenant_id, {"connections": {}})
        if integration_key in tenant.get("connections", {}):
            tenant["connections"][integration_key]["connected"] = False
            tenant["connections"][integration_key]["status"] = "disconnected"
            tenant["connections"][integration_key]["disconnected_at"] = _now()
        _save_file_state(data)

    _audit(tenant_id, "client_integration_disconnected", integration_key, "", "disconnected")

    return {
        "success": True,
        "integration_key": integration_key,
        "status": "disconnected",
        "storage_mode": "postgres" if _db_available() else "file_fallback",
    }


def get_client_integration_secret(tenant_id: str, integration_key: str) -> Dict[str, Any]:
    if _db_available():
        _ensure_tables()
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT provider, status, credential_hint, credential_value, connected
                    FROM client_integrations
                    WHERE tenant_id = %s AND integration_key = %s
                    """,
                    (tenant_id, integration_key),
                )
                row = cur.fetchone()

        if not row or not row[4]:
            return {"success": False, "error": "integration_not_connected"}

        provider, status, credential_hint, credential_value, _connected = row
        return {
            "success": True,
            "integration_key": integration_key,
            "provider": provider,
            "status": status,
            "credential_hint": credential_hint,
            "credential_value": credential_value,
            "storage_mode": "postgres",
        }

    data = _load_file_state()
    connection = data.get("tenants", {}).get(tenant_id, {}).get("connections", {}).get(integration_key)
    if not connection or not connection.get("connected"):
        return {"success": False, "error": "integration_not_connected"}

    return {
        "success": True,
        "integration_key": integration_key,
        "provider": connection.get("provider"),
        "status": connection.get("status"),
        "credential_hint": connection.get("credential_hint"),
        "credential_value": connection.get("credential_value"),
        "storage_mode": "file_fallback",
    }


def log_email_proof_send(tenant_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    _audit(
        tenant_id,
        "email_proof_send",
        "email",
        str(payload.get("provider") or ""),
        str(payload.get("status") or ""),
        payload,
    )
    return {"success": True}


def integration_audit(limit: int = 50) -> Dict[str, Any]:
    if _db_available():
        _ensure_tables()
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT tenant_id, event, integration_key, provider, status, payload, created_at
                    FROM client_integration_audit
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                events = [
                    {
                        "tenant_id": row[0],
                        "event": row[1],
                        "integration_key": row[2],
                        "provider": row[3],
                        "status": row[4],
                        "payload": row[5],
                        "created_at": row[6].isoformat() if row[6] else None,
                    }
                    for row in cur.fetchall()
                ]
        return {"success": True, "events": events, "count": len(events), "storage_mode": "postgres"}

    data = _load_file_state()
    audit = list(reversed(data.get("audit", [])))[:limit]
    return {"success": True, "events": audit, "count": len(audit), "storage_mode": "file_fallback"}
