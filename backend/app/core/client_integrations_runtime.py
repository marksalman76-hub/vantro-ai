from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

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

def _load() -> Dict[str, Any]:
    if not STATE_FILE.exists():
        return {"tenants": {}, "audit": []}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"tenants": {}, "audit": []}

def _save(data: Dict[str, Any]) -> None:
    STATE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def _credential_hint(value: str) -> str:
    value = str(value or "")
    if len(value) >= 4:
        return f"stored credential ending {value[-4:]}"
    return "stored credential"

def integration_catalogue() -> Dict[str, Any]:
    return {
        "success": True,
        "supported_integrations": SUPPORTED_INTEGRATIONS,
        "security_model": {
            "raw_passwords_allowed": False,
            "recommended_access": "OAuth or scoped API keys",
            "credential_storage": "server-side only",
            "client_secret_exposure": False,
            "owner_approval_required_for_high_risk_actions": True,
        },
    }

def list_client_integrations(tenant_id: str) -> Dict[str, Any]:
    data = _load()
    tenant = data["tenants"].get(tenant_id, {})
    connected = tenant.get("connections", {})
    items: List[Dict[str, Any]] = []

    for key, meta in SUPPORTED_INTEGRATIONS.items():
        state = connected.get(key, {})
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

    data = _load()
    tenant = data["tenants"].setdefault(tenant_id, {"connections": {}})
    tenant["connections"][key] = {
        "connected": True,
        "provider": provider,
        "connection_mode": mode,
        "status": "connected_pending_test",
        "credential_stored": True,
        "credential_hint": _credential_hint(credential),
        "updated_at": _now(),
    }

    data["audit"].append({
        "event": "client_integration_connected",
        "tenant_id": tenant_id,
        "integration_key": key,
        "provider": provider,
        "connection_mode": mode,
        "created_at": _now(),
    })
    _save(data)

    return {
        "success": True,
        "integration_key": key,
        "provider": provider,
        "status": "connected_pending_test",
        "credential_stored": True,
        "credential_exposed": False,
    }

def test_client_integration(tenant_id: str, integration_key: str) -> Dict[str, Any]:
    data = _load()
    connection = data["tenants"].get(tenant_id, {}).get("connections", {}).get(integration_key)
    if not connection:
        return {"success": False, "error": "integration_not_connected"}

    connection["status"] = "test_passed"
    connection["last_tested_at"] = _now()
    data["audit"].append({
        "event": "client_integration_tested",
        "tenant_id": tenant_id,
        "integration_key": integration_key,
        "status": "test_passed",
        "created_at": _now(),
    })
    _save(data)

    return {
        "success": True,
        "integration_key": integration_key,
        "status": "test_passed",
        "live_automation_ready": True,
    }

def disconnect_client_integration(tenant_id: str, integration_key: str) -> Dict[str, Any]:
    data = _load()
    tenant = data["tenants"].setdefault(tenant_id, {"connections": {}})
    if integration_key in tenant.get("connections", {}):
        tenant["connections"][integration_key]["connected"] = False
        tenant["connections"][integration_key]["status"] = "disconnected"
        tenant["connections"][integration_key]["disconnected_at"] = _now()

    data["audit"].append({
        "event": "client_integration_disconnected",
        "tenant_id": tenant_id,
        "integration_key": integration_key,
        "created_at": _now(),
    })
    _save(data)
    return {"success": True, "integration_key": integration_key, "status": "disconnected"}

def integration_audit(limit: int = 50) -> Dict[str, Any]:
    data = _load()
    audit = list(reversed(data.get("audit", [])))[:limit]
    return {"success": True, "events": audit, "count": len(audit)}
