from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import base64
import hashlib
import json
import mimetypes
import shutil
import uuid


ROOT = Path(__file__).resolve().parents[3]
LOCAL_MEDIA_ASSET_DIR = ROOT / "runtime_outputs" / "durable_media_assets"
LOCAL_MEDIA_ASSET_DIR.mkdir(parents=True, exist_ok=True)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_id(prefix: str = "media_asset") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def safe_filename(value: str) -> str:
    cleaned = "".join(ch for ch in str(value or "") if ch.isalnum() or ch in {"_", "-", ".", "/"})
    cleaned = cleaned.replace("..", "").strip("/\\")
    return cleaned or safe_id()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class DurableMediaAsset:
    asset_id: str
    job_id: str = ""
    tenant_id: str = ""
    client_id: str = ""
    asset_type: str = "unknown"
    storage_backend: str = "local_dev"
    storage_key: str = ""
    filename: str = ""
    content_type: str = "application/octet-stream"
    size_bytes: int = 0
    checksum_sha256: str = ""
    preview_url: str = ""
    signed_url: str = ""
    public_url: str = ""
    metadata: Dict[str, Any] = None
    customer_safe: bool = True
    credential_values_exposed: bool = False
    internal_config_exposed: bool = False
    created_at: str = ""

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if not self.created_at:
            self.created_at = utc_now()


class LocalDurableMediaAssetStore:
    """
    Local implementation of the production MediaAssetStore contract.

    Production swap target:
    - S3 for bytes
    - RDS PostgreSQL for asset metadata
    - signed URLs for client/admin delivery

    This local version intentionally stores only file paths and local preview URLs.
    Do not store provider credentials or secrets in asset metadata.
    """

    def __init__(self, root: Optional[Path] = None):
        self.root = Path(root or LOCAL_MEDIA_ASSET_DIR)
        self.asset_root = self.root / "objects"
        self.meta_root = self.root / "metadata"
        self.asset_root.mkdir(parents=True, exist_ok=True)
        self.meta_root.mkdir(parents=True, exist_ok=True)

    def _asset_path(self, storage_key: str) -> Path:
        path = self.asset_root / safe_filename(storage_key)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def _meta_path(self, asset_id: str) -> Path:
        return self.meta_root / f"{safe_filename(asset_id)}.json"

    def save_bytes(
        self,
        data: bytes,
        filename: str,
        asset_type: str,
        job_id: str = "",
        tenant_id: str = "",
        client_id: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        content_type: str = "",
    ) -> Dict[str, Any]:
        asset_id = safe_id("durable_media_asset")
        filename = safe_filename(filename)
        content_type = content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
        storage_key = f"{job_id or 'unassigned'}/{asset_id}/{filename}"
        path = self._asset_path(storage_key)
        path.write_bytes(data)

        asset = DurableMediaAsset(
            asset_id=asset_id,
            job_id=job_id,
            tenant_id=tenant_id,
            client_id=client_id,
            asset_type=asset_type,
            storage_backend="local_dev",
            storage_key=storage_key,
            filename=filename,
            content_type=content_type,
            size_bytes=len(data),
            checksum_sha256=sha256_bytes(data),
            preview_url=f"local://durable_media_assets/{storage_key}",
            signed_url=f"local://durable_media_assets/{storage_key}",
            metadata=dict(metadata or {}),
            customer_safe=True,
            credential_values_exposed=False,
            internal_config_exposed=False,
        )
        return self.save_metadata(asdict(asset))

    def save_file(
        self,
        source_path: str,
        asset_type: str,
        job_id: str = "",
        tenant_id: str = "",
        client_id: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        filename: str = "",
        content_type: str = "",
    ) -> Dict[str, Any]:
        src = Path(source_path)
        if not src.exists() or not src.is_file():
            return {
                "success": False,
                "status": "source_file_not_found",
                "source_path": str(source_path),
                "customer_safe": True,
                "credential_values_exposed": False,
            }

        data = src.read_bytes()
        return self.save_bytes(
            data=data,
            filename=filename or src.name,
            asset_type=asset_type,
            job_id=job_id,
            tenant_id=tenant_id,
            client_id=client_id,
            metadata=metadata,
            content_type=content_type,
        )

    def save_base64(
        self,
        b64_data: str,
        filename: str,
        asset_type: str,
        job_id: str = "",
        tenant_id: str = "",
        client_id: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        content_type: str = "",
    ) -> Dict[str, Any]:
        try:
            if "," in b64_data and "base64" in b64_data.split(",", 1)[0]:
                b64_data = b64_data.split(",", 1)[1]
            data = base64.b64decode(b64_data)
        except Exception as error:
            return {
                "success": False,
                "status": "invalid_base64",
                "error": str(error)[:300],
                "customer_safe": True,
                "credential_values_exposed": False,
            }

        return self.save_bytes(
            data=data,
            filename=filename,
            asset_type=asset_type,
            job_id=job_id,
            tenant_id=tenant_id,
            client_id=client_id,
            metadata=metadata,
            content_type=content_type,
        )

    def save_metadata(self, asset: Dict[str, Any]) -> Dict[str, Any]:
        clean = dict(asset or {})
        clean["asset_id"] = str(clean.get("asset_id") or safe_id("durable_media_asset"))
        clean["customer_safe"] = True
        clean["credential_values_exposed"] = False
        clean["internal_config_exposed"] = False
        clean.setdefault("created_at", utc_now())

        path = self._meta_path(clean["asset_id"])
        temp = path.with_suffix(".json.tmp")
        temp.write_text(json.dumps(clean, indent=2, default=str), encoding="utf-8")
        temp.replace(path)
        return {"success": True, **clean}

    def get_asset(self, asset_id: str) -> Dict[str, Any]:
        path = self._meta_path(asset_id)
        if not path.exists():
            return {
                "success": False,
                "asset_id": asset_id,
                "status": "not_found",
                "customer_safe": True,
                "credential_values_exposed": False,
            }

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return {
                "success": True,
                **data,
                "customer_safe": True,
                "credential_values_exposed": False,
                "internal_config_exposed": False,
            }
        except Exception as error:
            return {
                "success": False,
                "asset_id": asset_id,
                "status": "read_failed",
                "error": str(error)[:300],
                "customer_safe": True,
                "credential_values_exposed": False,
            }

    def get_asset_bytes(self, asset_id: str) -> Dict[str, Any]:
        asset = self.get_asset(asset_id)
        if not asset.get("success"):
            return asset

        path = self._asset_path(asset.get("storage_key") or "")
        if not path.exists():
            return {
                "success": False,
                "asset_id": asset_id,
                "status": "object_not_found",
                "customer_safe": True,
                "credential_values_exposed": False,
            }

        data = path.read_bytes()
        return {
            "success": True,
            "asset": asset,
            "bytes": data,
            "size_bytes": len(data),
            "checksum_sha256": sha256_bytes(data),
            "customer_safe": True,
            "credential_values_exposed": False,
        }

    def list_assets(self, job_id: str = "", limit: int = 50) -> Dict[str, Any]:
        files = sorted(self.meta_root.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        assets = []
        for path in files:
            if len(assets) >= max(1, int(limit)):
                break
            try:
                asset = json.loads(path.read_text(encoding="utf-8"))
                if job_id and asset.get("job_id") != job_id:
                    continue
                asset["customer_safe"] = True
                asset["credential_values_exposed"] = False
                assets.append(asset)
            except Exception:
                continue

        return {
            "success": True,
            "count": len(assets),
            "assets": assets,
            "customer_safe": True,
            "credential_values_exposed": False,
        }

    def create_signed_url(self, asset_id: str, expires_seconds: int = 3600) -> Dict[str, Any]:
        asset = self.get_asset(asset_id)
        if not asset.get("success"):
            return asset

        # Local dev placeholder. Production implementation will generate an S3 pre-signed URL.
        return {
            "success": True,
            "asset_id": asset_id,
            "signed_url": asset.get("signed_url") or asset.get("preview_url") or "",
            "expires_seconds": expires_seconds,
            "storage_backend": asset.get("storage_backend") or "local_dev",
            "customer_safe": True,
            "credential_values_exposed": False,
        }


def get_media_asset_store() -> LocalDurableMediaAssetStore:
    return LocalDurableMediaAssetStore()
