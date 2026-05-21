from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
MEDIA_REGISTRY_FILE = DATA_DIR / "durable_media_registry.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not MEDIA_REGISTRY_FILE.exists():
        MEDIA_REGISTRY_FILE.write_text(
            json.dumps({"assets": [], "deliverables": []}, indent=2),
            encoding="utf-8",
        )


def _read() -> Dict[str, Any]:
    _ensure_store()
    try:
        data = json.loads(MEDIA_REGISTRY_FILE.read_text(encoding="utf-8"))
    except Exception:
        data = {"assets": [], "deliverables": []}

    data.setdefault("assets", [])
    data.setdefault("deliverables", [])
    return data


def _write(data: Dict[str, Any]) -> None:
    _ensure_store()
    MEDIA_REGISTRY_FILE.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def register_media_asset(
    *,
    tenant_id: str,
    url: str,
    title: str = "",
    asset_type: str = "media",
    source: str = "runtime",
    mime_type: str = "",
    size: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if not tenant_id:
        raise ValueError("tenant_id is required")
    if not url:
        raise ValueError("url is required")

    data = _read()
    asset = {
        "id": f"asset_{uuid.uuid4().hex[:12]}",
        "tenant_id": tenant_id,
        "url": url,
        "image_url": url if asset_type in {"image", "generated_image", "preview"} else "",
        "src": url,
        "title": title or "Media asset",
        "name": title or "Media asset",
        "type": asset_type,
        "source": source,
        "mime_type": mime_type,
        "size": size,
        "metadata": metadata or {},
        "created_at": _now(),
    }

    data["assets"].append(asset)
    _write(data)
    return asset


def list_media_assets(tenant_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    data = _read()
    assets = [a for a in data["assets"] if a.get("tenant_id") == tenant_id]
    assets.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return assets[:limit]


def persist_deliverable(
    *,
    tenant_id: str,
    execution_id: str,
    deliverable: Dict[str, Any],
    assets: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    if not tenant_id:
        raise ValueError("tenant_id is required")

    data = _read()
    record = {
        "id": f"deliverable_{uuid.uuid4().hex[:12]}",
        "tenant_id": tenant_id,
        "execution_id": execution_id or f"execution_{uuid.uuid4().hex[:10]}",
        "deliverable": deliverable or {},
        "assets": assets or deliverable.get("assets") or deliverable.get("images") or [],
        "created_at": _now(),
    }

    merged = dict(record["deliverable"])
    if record["assets"]:
        merged["assets"] = record["assets"]
        first = record["assets"][0]
        first_url = first.get("url") or first.get("image_url") or first.get("src")
        if first_url and not merged.get("image_url"):
            merged["image_url"] = first_url
        if first_url and not merged.get("preview_url"):
            merged["preview_url"] = first_url
        if first_url and not merged.get("download_url"):
            merged["download_url"] = first_url

    record["deliverable"] = merged
    data["deliverables"].append(record)
    _write(data)
    return record


def latest_deliverable(tenant_id: str) -> Optional[Dict[str, Any]]:
    data = _read()
    items = [d for d in data["deliverables"] if d.get("tenant_id") == tenant_id]
    if not items:
        return None
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return items[0]


def media_persistence_status() -> Dict[str, Any]:
    data = _read()
    return {
        "success": True,
        "storage_mode": "local_durable_registry_ready",
        "production_storage_ready_path": "supabase_r2_s3_adapter_next",
        "registry_file": str(MEDIA_REGISTRY_FILE),
        "asset_count": len(data["assets"]),
        "deliverable_count": len(data["deliverables"]),
    }
