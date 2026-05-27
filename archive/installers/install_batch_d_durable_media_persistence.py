from pathlib import Path
import json
import re
from datetime import datetime, timezone

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
APP = ROOT / "backend" / "app"
MEDIA_DIR = APP / "media"
API_DIR = APP / "api"
DATA_DIR = APP / "data"
BACKUPS = ROOT / "backups"

for p in [MEDIA_DIR, API_DIR, DATA_DIR, BACKUPS]:
    p.mkdir(parents=True, exist_ok=True)

durable_media_store = r'''from __future__ import annotations

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
'''

media_routes = r'''from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from backend.app.media.durable_media_store import (
    latest_deliverable,
    list_media_assets,
    media_persistence_status,
    persist_deliverable,
    register_media_asset,
)

router = APIRouter(prefix="/media", tags=["media"])


class RegisterAssetRequest(BaseModel):
    url: str
    title: str = ""
    asset_type: str = "media"
    source: str = "runtime"
    mime_type: str = ""
    size: str = ""
    metadata: Dict[str, Any] = {}


class PersistDeliverableRequest(BaseModel):
    execution_id: str = ""
    deliverable: Dict[str, Any]
    assets: list[Dict[str, Any]] = []


def _tenant(x_tenant_id: Optional[str]) -> str:
    tenant_id = x_tenant_id or "client_demo_001"
    if not tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id_required")
    return tenant_id


@router.get("/status")
def media_status():
    return media_persistence_status()


@router.post("/assets/register")
def register_asset(payload: RegisterAssetRequest, x_tenant_id: Optional[str] = Header(default=None)):
    asset = register_media_asset(
        tenant_id=_tenant(x_tenant_id),
        url=payload.url,
        title=payload.title,
        asset_type=payload.asset_type,
        source=payload.source,
        mime_type=payload.mime_type,
        size=payload.size,
        metadata=payload.metadata,
    )
    return {"success": True, "asset": asset}


@router.get("/assets")
def list_assets(x_tenant_id: Optional[str] = Header(default=None)):
    return {"success": True, "assets": list_media_assets(_tenant(x_tenant_id))}


@router.post("/deliverables/persist")
def persist(payload: PersistDeliverableRequest, x_tenant_id: Optional[str] = Header(default=None)):
    record = persist_deliverable(
        tenant_id=_tenant(x_tenant_id),
        execution_id=payload.execution_id,
        deliverable=payload.deliverable,
        assets=payload.assets,
    )
    return {"success": True, "record": record, "deliverable": record["deliverable"]}


@router.get("/deliverables/latest")
def latest(x_tenant_id: Optional[str] = Header(default=None)):
    record = latest_deliverable(_tenant(x_tenant_id))
    return {
        "success": True,
        "record": record,
        "deliverable": record.get("deliverable") if record else None,
    }
'''

test_script = r'''import json
from backend.app.media.durable_media_store import (
    latest_deliverable,
    list_media_assets,
    media_persistence_status,
    persist_deliverable,
    register_media_asset,
)

TENANT = "client_batch_d_media_test"

asset = register_media_asset(
    tenant_id=TENANT,
    url="https://example.com/demo-product-image.png",
    title="Demo product image",
    asset_type="generated_image",
    source="batch_d_test",
    mime_type="image/png",
)

record = persist_deliverable(
    tenant_id=TENANT,
    execution_id="execution_batch_d_test",
    deliverable={
        "title": "Batch D durable media deliverable",
        "summary": "Durable media metadata and deliverable persistence are working.",
        "tags": ["Durable media", "Deliverable persistence", "Launch QA"],
    },
    assets=[asset],
)

latest = latest_deliverable(TENANT)
assets = list_media_assets(TENANT)
status = media_persistence_status()

results = {
    "asset_registered": bool(asset.get("id")),
    "deliverable_persisted": bool(record.get("id")),
    "latest_deliverable_found": bool(latest and latest.get("deliverable")),
    "image_url_bound": latest["deliverable"].get("image_url") == asset["url"],
    "download_url_bound": latest["deliverable"].get("download_url") == asset["url"],
    "asset_count_for_tenant": len(assets),
    "status": status,
}

print("BATCH_D_DURABLE_MEDIA_RESULTS")
print(json.dumps(results, indent=2))

if not all([
    results["asset_registered"],
    results["deliverable_persisted"],
    results["latest_deliverable_found"],
    results["image_url_bound"],
    results["download_url_bound"],
]):
    raise SystemExit("BATCH_D_FAILED")

print("BATCH_D_DURABLE_MEDIA_OK")
'''

(MEDIA_DIR / "durable_media_store.py").write_text(durable_media_store, encoding="utf-8")
(API_DIR / "media_routes.py").write_text(media_routes, encoding="utf-8")
(ROOT / "test_batch_d_durable_media_persistence.py").write_text(test_script, encoding="utf-8")

main_path = APP / "main.py"
if main_path.exists():
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup = BACKUPS / f"main_before_batch_d_media_{stamp}.py"
    backup.write_text(main_path.read_text(encoding="utf-8"), encoding="utf-8")

    text = main_path.read_text(encoding="utf-8")

    if "backend.app.api.media_routes import router as media_router" not in text:
        text = "from backend.app.api.media_routes import router as media_router\n" + text

    if "app.include_router(media_router)" not in text:
        marker = "app = FastAPI"
        if marker in text:
            # Safer: append include after whole file if app is globally defined.
            text = text.rstrip() + "\n\n# Batch D durable media routes\napp.include_router(media_router)\n"
        else:
            text = text.rstrip() + "\n\n# Batch D durable media routes\napp.include_router(media_router)\n"

    main_path.write_text(text, encoding="utf-8")
    print(f"Updated main.py")
    print(f"Backup: {backup}")

print("BATCH_D_DURABLE_MEDIA_PERSISTENCE_INSTALLED")
print("Created: backend\\app\\media\\durable_media_store.py")
print("Created: backend\\app\\api\\media_routes.py")
print("Created: test_batch_d_durable_media_persistence.py")