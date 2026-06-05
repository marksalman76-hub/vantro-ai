from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA_DIR = Path(os.getenv("ADMIN_INDUSTRY_STORE_DIR", "data/admin_industry_store"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

INDUSTRY_STORE = DATA_DIR / "industry_agent_store.json"
LEARNING_VAULT = DATA_DIR / "tenant_safe_learning_vault.jsonl"

SENSITIVE_KEYS = {
    "email",
    "phone",
    "address",
    "customer_name",
    "client_name",
    "business_name",
    "api_key",
    "token",
    "secret",
    "password",
    "raw_output",
    "raw_prompt",
    "private_notes",
    "credential",
}


def _now() -> int:
    return int(time.time())


def _load_store() -> Dict[str, Any]:
    if not INDUSTRY_STORE.exists():
        return {"industry_packs": []}
    try:
        return json.loads(INDUSTRY_STORE.read_text(encoding="utf-8"))
    except Exception:
        return {"industry_packs": []}


def _save_store(data: Dict[str, Any]) -> None:
    INDUSTRY_STORE.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _safe_text(value: Any, limit: int = 2000) -> str:
    text = str(value or "")
    for token in ["api key", "secret", "password", "token", "credential"]:
        text = text.replace(token, "[redacted]")
        text = text.replace(token.upper(), "[redacted]")
    return text[:limit]


def _tenant_safe_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    safe: Dict[str, Any] = {}
    for key, value in payload.items():
        lowered = str(key).lower()
        if lowered in SENSITIVE_KEYS or any(s in lowered for s in ["secret", "password", "token", "credential", "email", "phone"]):
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            safe[key] = _safe_text(value) if isinstance(value, str) else value
        elif isinstance(value, list):
            safe[key] = [_safe_text(x, 500) if isinstance(x, str) else x for x in value[:20]]
        elif isinstance(value, dict):
            safe[key] = _tenant_safe_payload(value)
    return safe


def create_or_update_industry_pack(payload: Dict[str, Any]) -> Dict[str, Any]:
    industry = _safe_text(payload.get("industry") or payload.get("industry_key") or "").strip().lower().replace(" ", "_")
    if not industry:
        return {"success": False, "error": "industry_required"}

    pack_id = payload.get("pack_id") or f"industry_pack_{industry}_{uuid.uuid4().hex[:10]}"
    agents = payload.get("agents") or payload.get("agent_ids") or []
    if not isinstance(agents, list):
        agents = []

    safe_pack = {
        "pack_id": pack_id,
        "industry": industry,
        "display_name": _safe_text(payload.get("display_name") or industry.replace("_", " ").title(), 160),
        "description": _safe_text(payload.get("description"), 1200),
        "agents": [
            {
                "agent_id": _safe_text(a.get("agent_id") if isinstance(a, dict) else a, 120),
                "role": _safe_text(a.get("role") if isinstance(a, dict) else "", 300),
                "default_instructions": _safe_text(a.get("default_instructions") if isinstance(a, dict) else "", 1200),
                "deployment_notes": _safe_text(a.get("deployment_notes") if isinstance(a, dict) else "", 1200),
            }
            for a in agents
        ],
        "recommended_integrations": [
            _safe_text(x, 120) for x in (payload.get("recommended_integrations") or [])[:25]
        ],
        "deployment_checklist": [
            _safe_text(x, 300) for x in (payload.get("deployment_checklist") or [])[:50]
        ],
        "owner_only": True,
        "tenant_safe": True,
        "updated_at": _now(),
        "created_at": _now(),
    }

    data = _load_store()
    packs = data.setdefault("industry_packs", [])
    for index, existing in enumerate(packs):
        if existing.get("pack_id") == pack_id or existing.get("industry") == industry:
            safe_pack["created_at"] = existing.get("created_at", safe_pack["created_at"])
            packs[index] = safe_pack
            _save_store(data)
            return {"success": True, "action": "updated", "pack": safe_pack}

    packs.insert(0, safe_pack)
    _save_store(data)
    return {"success": True, "action": "created", "pack": safe_pack}


def list_industry_packs(industry: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
    packs = _load_store().get("industry_packs", [])
    if industry:
        needle = industry.lower().replace(" ", "_")
        packs = [p for p in packs if p.get("industry") == needle]
    return {"success": True, "count": len(packs[:limit]), "industry_packs": packs[:limit]}


def capture_tenant_safe_learning(payload: Dict[str, Any]) -> Dict[str, Any]:
    agent_id = _safe_text(payload.get("agent_id") or payload.get("requested_agent") or "unknown_agent", 120)
    industry = _safe_text(payload.get("industry") or payload.get("business_niche") or "general", 120).lower().replace(" ", "_")
    quality_score = payload.get("quality_score")
    try:
        quality_score = int(quality_score) if quality_score is not None else None
    except Exception:
        quality_score = None

    record = {
        "vault_id": f"learning_vault_{uuid.uuid4().hex[:14]}",
        "industry": industry,
        "agent_id": agent_id,
        "client_type": _safe_text(payload.get("client_type") or payload.get("package_name") or "", 160),
        "pattern_type": _safe_text(payload.get("pattern_type") or "execution_learning", 120),
        "successful_patterns": [_safe_text(x, 600) for x in (payload.get("successful_patterns") or [])[:20]],
        "failed_patterns": [_safe_text(x, 600) for x in (payload.get("failed_patterns") or [])[:20]],
        "recommended_improvements": [_safe_text(x, 700) for x in (payload.get("recommended_improvements") or [])[:20]],
        "quality_score": quality_score,
        "approved_by_client": bool(payload.get("approved_by_client")),
        "source": _safe_text(payload.get("source") or "agent_execution", 120),
        "tenant_safe_summary": _safe_text(payload.get("tenant_safe_summary") or payload.get("summary"), 2000),
        "reusable_template": _safe_text(payload.get("reusable_template"), 3000),
        "raw_private_data_stored": False,
        "tenant_safe": True,
        "owner_only": True,
        "created_at": _now(),
        "safe_metadata": _tenant_safe_payload(payload.get("metadata") or {}),
    }

    with LEARNING_VAULT.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")

    return {
        "success": True,
        "vault_id": record["vault_id"],
        "tenant_safe": True,
        "raw_private_data_stored": False,
        "record": record,
    }


def list_learning_vault(
    industry: Optional[str] = None,
    agent_id: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    if LEARNING_VAULT.exists():
        for line in LEARNING_VAULT.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue

    if industry:
        needle = industry.lower().replace(" ", "_")
        rows = [r for r in rows if r.get("industry") == needle]
    if agent_id:
        rows = [r for r in rows if r.get("agent_id") == agent_id]

    rows = list(reversed(rows))
    return {"success": True, "count": len(rows[:limit]), "learning_records": rows[:limit]}


def admin_industry_learning_vault_status() -> Dict[str, Any]:
    pack_count = len(_load_store().get("industry_packs", []))
    learning_count = 0
    if LEARNING_VAULT.exists():
        learning_count = len([line for line in LEARNING_VAULT.read_text(encoding="utf-8").splitlines() if line.strip()])

    return {
        "success": True,
        "admin_industry_agent_store_ready": True,
        "tenant_safe_learning_vault_ready": True,
        "industry_pack_count": pack_count,
        "learning_record_count": learning_count,
        "owner_only": True,
        "raw_private_data_stored": False,
        "future_deployment_reuse_ready": True,
    }
