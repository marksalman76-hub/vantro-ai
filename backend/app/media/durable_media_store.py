from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.app.runtime.canonical_media_asset_metadata_runtime import (
    get_media_asset_metadata_summary,
    link_asset_to_deliverable,
    list_deliverable_assets,
    list_media_assets as canonical_list_media_assets,
    record_media_asset,
)

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

    asset_id = f"asset_{uuid.uuid4().hex[:12]}"
    canonical = record_media_asset(
        asset_id=asset_id,
        tenant_id=tenant_id,
        asset_type=asset_type,
        media_type=asset_type,
        status="registered",
        storage_provider="provider_url" if url.startswith(("http://", "https://")) else "local_runtime_file",
        provider_url=url if url.startswith(("http://", "https://")) else "",
        local_path="" if url.startswith(("http://", "https://")) else url,
        preview_url=url,
        download_url=url,
        mime_type=mime_type,
        byte_size=int(size) if str(size or "").isdigit() else None,
        preview_ready=True,
        download_ready=True,
        playable=True,
        metadata_only=False,
        source_runtime="durable_media_store",
        payload={
            "title": title or "Media asset",
            "source": source,
            "metadata": metadata or {},
        },
    )
    if not canonical.get("success"):
        return {
            "success": False,
            "status": canonical.get("status", "canonical_media_metadata_unavailable"),
            "error": canonical.get("reason"),
            "authority": "backend_canonical",
            "production_fail_closed": bool(canonical.get("production_fail_closed")),
            "credential_values_exposed": False,
            "customer_safe": True,
        }

    data = _read()
    asset = {
        "id": asset_id,
        "asset_id": asset_id,
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
        "authority": "backend_canonical",
        "canonical_storage_mode": canonical.get("storage_mode"),
        "dev_only": bool(canonical.get("dev_only")),
        "fallback_used": False,
        "production_fail_closed": False,
        "credential_values_exposed": False,
    }

    if canonical.get("dev_only"):
        data["assets"].append({**asset, "authority": "frontend_advisory", "fallback_used": True})
        _write(data)
    return asset


def list_media_assets(tenant_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    canonical = canonical_list_media_assets(tenant_id=tenant_id, limit=limit)
    if canonical.get("success"):
        assets: List[Dict[str, Any]] = []
        for item in canonical.get("assets", []):
            if not isinstance(item, dict):
                continue
            url = item.get("preview_url") or item.get("download_url") or item.get("provider_url") or item.get("local_path") or ""
            payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}
            assets.append(
                {
                    "id": item.get("asset_id"),
                    "asset_id": item.get("asset_id"),
                    "tenant_id": item.get("tenant_id"),
                    "url": url,
                    "image_url": url if item.get("asset_type") in {"image", "generated_image", "preview"} else "",
                    "src": url,
                    "title": payload.get("title") or "Media asset",
                    "name": payload.get("title") or "Media asset",
                    "type": item.get("asset_type") or item.get("media_type") or "media",
                    "source": payload.get("source") or item.get("source_runtime"),
                    "mime_type": item.get("mime_type") or "",
                    "size": str(item.get("byte_size") or ""),
                    "metadata": payload.get("metadata") or item.get("payload") or {},
                    "created_at": item.get("created_at"),
                    "preview_ready": bool(item.get("preview_ready")),
                    "download_ready": bool(item.get("download_ready")),
                    "playable": bool(item.get("playable")),
                    "metadata_only": bool(item.get("metadata_only")),
                    "authority": "backend_canonical",
                    "canonical_storage_mode": canonical.get("storage_mode"),
                    "dev_only": bool(canonical.get("dev_only")),
                    "fallback_used": False,
                    "production_fail_closed": False,
                    "credential_values_exposed": False,
                }
            )
        return assets

    if canonical.get("production_fail_closed"):
        return []

    data = _read()
    assets = [a for a in data["assets"] if a.get("tenant_id") == tenant_id]
    assets.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return [
        {
            **asset,
            "authority": "frontend_advisory",
            "fallback_used": True,
            "dev_only": True,
            "production_fail_closed": False,
            "credential_values_exposed": False,
        }
        for asset in assets[:limit]
    ]


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
    canonical_assets: List[Dict[str, Any]] = []
    for asset in record["assets"]:
        if not isinstance(asset, dict):
            continue
        asset_url = asset.get("url") or asset.get("image_url") or asset.get("src") or asset.get("preview_url") or asset.get("download_url") or ""
        if not asset_url:
            continue
        canonical_asset = record_media_asset(
            asset_id=asset.get("asset_id") or asset.get("id") or f"asset_{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            execution_id=record["execution_id"],
            asset_type=asset.get("asset_type") or asset.get("type") or "deliverable_asset",
            media_type=asset.get("media_type") or asset.get("type") or "deliverable_asset",
            status="linked_to_deliverable",
            storage_provider="provider_url" if str(asset_url).startswith(("http://", "https://")) else "local_runtime_file",
            provider_url=asset_url if str(asset_url).startswith(("http://", "https://")) else "",
            local_path="" if str(asset_url).startswith(("http://", "https://")) else asset_url,
            preview_url=asset.get("preview_url") or asset_url,
            download_url=asset.get("download_url") or asset_url,
            mime_type=asset.get("mime_type") or "",
            preview_ready=True,
            download_ready=True,
            playable=True,
            metadata_only=False,
            source_runtime="durable_media_store",
            payload=asset,
        )
        if canonical_asset.get("success"):
            item = canonical_asset.get("asset") or {}
            canonical_assets.append(item)
            link_asset_to_deliverable(
                tenant_id=tenant_id,
                execution_id=record["execution_id"],
                deliverable_id=record["id"],
                asset_id=item.get("asset_id") or asset.get("id"),
                link_type="latest_deliverable_asset",
            )
        elif canonical_asset.get("production_fail_closed"):
            return {
                **record,
                "success": False,
                "status": canonical_asset.get("status"),
                "authority": "backend_canonical",
                "production_fail_closed": True,
                "credential_values_exposed": False,
            }

    record["authority"] = "backend_canonical"
    record["canonical_asset_count"] = len(canonical_assets)
    record["fallback_used"] = False
    record["production_fail_closed"] = False
    record["credential_values_exposed"] = False
    if any(asset.get("dev_only") for asset in canonical_assets):
        data["deliverables"].append({**record, "authority": "frontend_advisory", "fallback_used": True, "dev_only": True})
        _write(data)
    return record


def latest_deliverable(tenant_id: str) -> Optional[Dict[str, Any]]:
    canonical = list_deliverable_assets(tenant_id=tenant_id, limit=100)
    if canonical.get("success") and canonical.get("assets"):
        assets = canonical.get("assets", [])
        return {
            "id": "",
            "tenant_id": tenant_id,
            "execution_id": (assets[0] or {}).get("execution_id") or "",
            "deliverable": {
                "assets": assets,
                "preview_url": (assets[0] or {}).get("preview_url"),
                "download_url": (assets[0] or {}).get("download_url"),
                "authority": "backend_canonical",
                "fallback_used": False,
                "dev_only": bool(canonical.get("dev_only")),
                "credential_values_exposed": False,
            },
            "assets": assets,
            "created_at": (assets[0] or {}).get("created_at"),
            "authority": "backend_canonical",
            "fallback_used": False,
            "dev_only": bool(canonical.get("dev_only")),
            "production_fail_closed": False,
            "credential_values_exposed": False,
        }
    if canonical.get("production_fail_closed"):
        return {
            "success": False,
            "status": canonical.get("status"),
            "tenant_id": tenant_id,
            "authority": "backend_canonical",
            "production_fail_closed": True,
            "credential_values_exposed": False,
        }

    data = _read()
    items = [d for d in data["deliverables"] if d.get("tenant_id") == tenant_id]
    if not items:
        return None
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {
        **items[0],
        "authority": "frontend_advisory",
        "fallback_used": True,
        "dev_only": True,
        "production_fail_closed": False,
        "credential_values_exposed": False,
    }


def media_persistence_status() -> Dict[str, Any]:
    data = _read()
    canonical = get_media_asset_metadata_summary()
    return {
        "success": bool(canonical.get("success", True)),
        "storage_mode": canonical.get("storage_mode") or "local_durable_registry_ready",
        "authority": "backend_canonical",
        "fallback_used": bool(canonical.get("dev_only")),
        "dev_only": bool(canonical.get("dev_only")),
        "production_fail_closed": bool(canonical.get("production_fail_closed")),
        "production_storage_ready_path": "supabase_r2_s3_adapter_next",
        "registry_file": str(MEDIA_REGISTRY_FILE),
        "asset_count": canonical.get("asset_count", len(data["assets"])),
        "deliverable_count": len(data["deliverables"]),
        "credential_values_exposed": False,
    }
