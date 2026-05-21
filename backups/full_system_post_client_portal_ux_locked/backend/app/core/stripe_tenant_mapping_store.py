from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

MAPPING_FILE = DATA_DIR / "stripe_tenant_mappings.json"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> Dict[str, Any]:
    if not MAPPING_FILE.exists():
        return {
            "version": "step203_stripe_tenant_mapping_v1",
            "mappings": [],
            "updated_at": utc_now_iso(),
        }

    try:
        return json.loads(MAPPING_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {
            "version": "step203_stripe_tenant_mapping_v1",
            "mappings": [],
            "updated_at": utc_now_iso(),
            "recovered_from_invalid_json": True,
        }


def _save(data: Dict[str, Any]) -> None:
    data["updated_at"] = utc_now_iso()
    MAPPING_FILE.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def upsert_stripe_tenant_mapping(
    tenant_id: str,
    stripe_customer_id: Optional[str] = None,
    stripe_subscription_id: Optional[str] = None,
    company_name: Optional[str] = None,
    subscription_status: Optional[str] = None,
    package_name: Optional[str] = None,
) -> Dict[str, Any]:
    if not tenant_id:
        raise ValueError("tenant_id_required")

    data = _load()
    mappings = data.setdefault("mappings", [])

    existing = None
    for item in mappings:
        if item.get("tenant_id") == tenant_id:
            existing = item
            break

    if existing is None:
        existing = {
            "tenant_id": tenant_id,
            "created_at": utc_now_iso(),
        }
        mappings.append(existing)

    if stripe_customer_id:
        existing["stripe_customer_id"] = stripe_customer_id

    if stripe_subscription_id:
        existing["stripe_subscription_id"] = stripe_subscription_id

    if company_name:
        existing["company_name"] = company_name

    if subscription_status:
        existing["subscription_status"] = subscription_status

    if package_name:
        existing["package_name"] = package_name

    existing["updated_at"] = utc_now_iso()
    _save(data)

    return {
        "success": True,
        "mapping": existing,
        "mapping_file": str(MAPPING_FILE),
    }


def resolve_tenant_by_stripe_ids(
    stripe_customer_id: Optional[str] = None,
    stripe_subscription_id: Optional[str] = None,
) -> Dict[str, Any]:
    data = _load()

    for item in data.get("mappings", []):
        if stripe_customer_id and item.get("stripe_customer_id") == stripe_customer_id:
            return {
                "success": True,
                "resolved": True,
                "match_type": "stripe_customer_id",
                "mapping": item,
            }

        if stripe_subscription_id and item.get("stripe_subscription_id") == stripe_subscription_id:
            return {
                "success": True,
                "resolved": True,
                "match_type": "stripe_subscription_id",
                "mapping": item,
            }

    return {
        "success": True,
        "resolved": False,
        "match_type": None,
        "mapping": None,
    }


def list_stripe_tenant_mappings(limit: int = 50) -> Dict[str, Any]:
    data = _load()
    mappings = data.get("mappings", [])[-limit:]

    return {
        "success": True,
        "count": len(mappings),
        "mappings": mappings,
        "mapping_file": str(MAPPING_FILE),
        "checked_at": utc_now_iso(),
    }
