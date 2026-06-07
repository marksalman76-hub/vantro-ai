from __future__ import annotations

import json
import os
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


CANONICAL_PRODUCT_ASSET_METADATA_PROFILE = "canonical_product_asset_metadata_runtime_v1"

_DEV_PRODUCT_ASSETS: Dict[str, Dict[str, Any]] = {}
_DEV_PRODUCT_ASSET_EVENTS: Dict[str, Dict[str, Any]] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _now_iso() -> str:
    return _now().isoformat()


def _database_url() -> str:
    return os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or ""


def _is_production() -> bool:
    values = [
        os.getenv("ENVIRONMENT"),
        os.getenv("APP_ENV"),
        os.getenv("FASTAPI_ENV"),
        os.getenv("NODE_ENV"),
        os.getenv("RENDER"),
        os.getenv("VERCEL_ENV"),
        os.getenv("PRODUCTION"),
    ]
    return any(str(value or "").strip().lower() in {"1", "true", "prod", "production"} for value in values)


def _psycopg():
    try:
        import psycopg  # type: ignore

        return psycopg
    except Exception:
        return None


def _connect():
    psycopg = _psycopg()
    if psycopg is None:
        raise RuntimeError("psycopg_unavailable")
    if not _database_url():
        raise RuntimeError("DATABASE_URL_missing")
    timeout = max(1, min(int(os.getenv("PRODUCT_ASSET_METADATA_CONNECT_TIMEOUT_SECONDS") or 2), 10))
    return psycopg.connect(_database_url(), connect_timeout=timeout)


def _safe_response(**payload: Any) -> Dict[str, Any]:
    result = dict(payload)
    result.setdefault("canonical_product_asset_metadata_profile", CANONICAL_PRODUCT_ASSET_METADATA_PROFILE)
    result.setdefault("authority", "backend_canonical")
    result.setdefault("fallback_used", False)
    result.setdefault("production_fail_closed", False)
    result.setdefault("credential_values_exposed", False)
    result.setdefault("customer_safe", True)
    return result


def _unavailable(reason: str) -> Dict[str, Any]:
    return _safe_response(
        success=False,
        status="canonical_product_asset_metadata_store_unavailable",
        product_asset_metadata_ready=False,
        durable=False,
        storage_mode="postgres_unavailable",
        production_fail_closed=_is_production(),
        dev_only=False,
        not_production_durable=False,
        reason=str(reason or "canonical_store_unavailable")[:1000],
    )


def _using_dev(readiness: Dict[str, Any]) -> bool:
    return readiness.get("storage_mode") == "dev_memory"


def _clean(value: Any, default: str = "") -> str:
    text = str(value or default).strip()
    return text or default


def _limit(value: int, default: int = 100, maximum: int = 1000) -> int:
    try:
        parsed = int(value or default)
    except Exception:
        parsed = default
    return max(1, min(parsed, maximum))


def _scrub_sensitive(data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    safe: Dict[str, Any] = {}
    for key, value in (data or {}).items():
        lowered = str(key).lower()
        if any(marker in lowered for marker in ("secret", "token", "api_key", "password", "credential", "authorization")):
            continue
        if isinstance(value, dict):
            safe[str(key)] = _scrub_sensitive(value)
        elif isinstance(value, list):
            safe[str(key)] = [_scrub_sensitive(item) if isinstance(item, dict) else item for item in value]
        else:
            safe[str(key)] = value
    return safe


def _json(data: Optional[Dict[str, Any]]) -> str:
    return json.dumps(_scrub_sensitive(deepcopy(data or {})), ensure_ascii=False, sort_keys=True)


def _parse_json(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return _scrub_sensitive(value)
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return _scrub_sensitive(parsed) if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    return {}


def _dt(value: Any) -> Any:
    return value.isoformat() if isinstance(value, datetime) else value


def _has_safe_url(value: Any) -> bool:
    text = str(value or "").strip()
    return text.startswith(("https://", "http://", "/"))


def _has_object_reference(record: Dict[str, Any]) -> bool:
    provider = str(record.get("storage_provider") or "").lower()
    return provider in {"supabase", "object_storage", "s3", "r2"} and bool(record.get("bucket")) and bool(record.get("object_key"))


def _normalise_product_asset_record(record: Dict[str, Any]) -> Dict[str, Any]:
    item = dict(record)
    item["payload"] = _scrub_sensitive(item.get("payload") or {})
    object_backed = _has_object_reference(item)
    preview_available = _has_safe_url(item.get("preview_url")) or object_backed
    download_available = _has_safe_url(item.get("download_url")) or object_backed
    item["preview_ready"] = bool(item.get("preview_ready")) and preview_available and not item.get("deleted_at")
    item["download_ready"] = bool(item.get("download_ready")) and download_available and not item.get("deleted_at")
    item["bucket"] = item.get("bucket") or ""
    item["object_key"] = item.get("object_key") or ""
    item["local_path"] = item.get("local_path") or ""
    item["storage_bucket"] = item["bucket"] or None
    item["storage_object_key"] = item["object_key"] or None
    item["stored_path"] = item["local_path"] or None
    item["stored_filename"] = item.get("stored_filename") or ""
    item["public_url"] = item.get("preview_url") or item.get("download_url") or None
    item["size_bytes"] = item.get("byte_size")
    item["sha256"] = item.get("checksum")
    item["campaign_id"] = item.get("project_id") or ""
    item["metadata"] = deepcopy(item["payload"])
    item["credential_values_exposed"] = False
    item["customer_safe"] = True
    return item


def _asset_columns() -> List[str]:
    return [
        "asset_id",
        "tenant_id",
        "project_id",
        "uploaded_by",
        "asset_type",
        "filename",
        "original_filename",
        "mime_type",
        "byte_size",
        "checksum",
        "storage_provider",
        "bucket",
        "object_key",
        "local_path",
        "preview_url",
        "download_url",
        "preview_ready",
        "download_ready",
        "status",
        "approval_status",
        "source_runtime",
        "payload_json",
        "created_at",
        "updated_at",
        "deleted_at",
        "credential_values_exposed",
    ]


def _event_columns() -> List[str]:
    return ["event_id", "asset_id", "tenant_id", "project_id", "event_type", "actor_role", "payload_json", "created_at"]


def _row(row: Any, columns: List[str]) -> Dict[str, Any]:
    result = dict(zip(columns, row))
    if "payload_json" in result:
        result["payload"] = _parse_json(result.pop("payload_json", None))
    for key, value in list(result.items()):
        result[key] = _dt(value)
    result["credential_values_exposed"] = False
    result["customer_safe"] = True
    if "asset_id" in result and "source_runtime" in result:
        return _normalise_product_asset_record(result)
    return result


def ensure_product_asset_metadata_tables() -> Dict[str, Any]:
    if not _database_url():
        if _is_production():
            return _unavailable("DATABASE_URL_missing")
        return _safe_response(
            success=True,
            status="dev_only_product_asset_metadata_ready",
            product_asset_metadata_ready=True,
            durable=False,
            storage_mode="dev_memory",
            persistence_mode="dev_only",
            dev_only=True,
            not_production_durable=True,
        )

    if _psycopg() is None:
        if _is_production():
            return _unavailable("psycopg_unavailable")
        return _safe_response(
            success=True,
            status="dev_only_product_asset_metadata_ready",
            product_asset_metadata_ready=True,
            durable=False,
            storage_mode="dev_memory",
            persistence_mode="dev_only",
            dev_only=True,
            not_production_durable=True,
            postgres_configured_but_driver_unavailable=True,
        )

    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS product_asset_records (
                        asset_id TEXT PRIMARY KEY,
                        tenant_id TEXT NOT NULL,
                        project_id TEXT NOT NULL DEFAULT 'default_project',
                        uploaded_by TEXT,
                        asset_type TEXT,
                        filename TEXT,
                        original_filename TEXT,
                        mime_type TEXT,
                        byte_size BIGINT,
                        checksum TEXT,
                        storage_provider TEXT,
                        bucket TEXT,
                        object_key TEXT,
                        local_path TEXT,
                        preview_url TEXT,
                        download_url TEXT,
                        preview_ready BOOLEAN NOT NULL DEFAULT FALSE,
                        download_ready BOOLEAN NOT NULL DEFAULT FALSE,
                        status TEXT NOT NULL DEFAULT 'recorded',
                        approval_status TEXT NOT NULL DEFAULT 'pending_review',
                        source_runtime TEXT,
                        payload_json JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        deleted_at TIMESTAMPTZ,
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_product_asset_records_tenant_created ON product_asset_records (tenant_id, created_at DESC)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_product_asset_records_project_created ON product_asset_records (project_id, created_at DESC)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_product_asset_records_type ON product_asset_records (tenant_id, asset_type, created_at DESC)")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS product_asset_events (
                        event_id TEXT PRIMARY KEY,
                        asset_id TEXT,
                        tenant_id TEXT NOT NULL,
                        project_id TEXT NOT NULL DEFAULT 'default_project',
                        event_type TEXT NOT NULL,
                        actor_role TEXT,
                        payload_json JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_product_asset_events_asset_created ON product_asset_events (asset_id, created_at DESC)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_product_asset_events_tenant_created ON product_asset_events (tenant_id, created_at DESC)")
            conn.commit()
        return _safe_response(success=True, status="product_asset_metadata_ready", product_asset_metadata_ready=True, durable=True, storage_mode="postgres", persistence_mode="postgres", dev_only=False, not_production_durable=False)
    except Exception as exc:
        if _is_production():
            return _unavailable(str(exc))
        return _safe_response(success=True, status="dev_only_product_asset_metadata_ready", product_asset_metadata_ready=True, durable=False, storage_mode="dev_memory", persistence_mode="dev_only", dev_only=True, not_production_durable=True, postgres_error=str(exc))


def record_product_asset(
    *,
    asset_id: str = "",
    tenant_id: str,
    project_id: str = "default_project",
    uploaded_by: str = "owner_admin",
    asset_type: str = "reference_asset",
    filename: str = "",
    original_filename: str = "",
    mime_type: str = "",
    byte_size: Optional[int] = None,
    checksum: str = "",
    storage_provider: str = "",
    bucket: str = "",
    object_key: str = "",
    local_path: str = "",
    preview_url: str = "",
    download_url: str = "",
    preview_ready: bool = False,
    download_ready: bool = False,
    status: str = "recorded",
    approval_status: str = "pending_review",
    source_runtime: str = "canonical_product_asset_metadata_runtime",
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    readiness = ensure_product_asset_metadata_tables()
    if not readiness.get("success"):
        return readiness

    record = _normalise_product_asset_record(
        {
            "asset_id": _clean(asset_id) or f"product_asset_{uuid.uuid4().hex[:18]}",
            "tenant_id": _clean(tenant_id, "owner_admin"),
            "project_id": _clean(project_id, "default_project"),
            "uploaded_by": _clean(uploaded_by, "owner_admin"),
            "asset_type": _clean(asset_type, "reference_asset"),
            "filename": _clean(filename, "uploaded_asset"),
            "original_filename": _clean(original_filename) or _clean(filename, "uploaded_asset"),
            "mime_type": _clean(mime_type, "application/octet-stream"),
            "byte_size": int(byte_size) if byte_size is not None and str(byte_size).strip() else None,
            "checksum": _clean(checksum),
            "storage_provider": _clean(storage_provider),
            "bucket": _clean(bucket),
            "object_key": _clean(object_key),
            "local_path": _clean(local_path),
            "preview_url": _clean(preview_url),
            "download_url": _clean(download_url),
            "preview_ready": bool(preview_ready),
            "download_ready": bool(download_ready),
            "status": _clean(status, "recorded"),
            "approval_status": _clean(approval_status, "pending_review"),
            "source_runtime": _clean(source_runtime, "canonical_product_asset_metadata_runtime"),
            "payload": _scrub_sensitive(payload or {}),
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
            "deleted_at": None,
            "credential_values_exposed": False,
            "customer_safe": True,
        }
    )

    if _using_dev(readiness):
        existing = _DEV_PRODUCT_ASSETS.get(record["asset_id"], {})
        record["created_at"] = existing.get("created_at") or record["created_at"]
        _DEV_PRODUCT_ASSETS[record["asset_id"]] = deepcopy(record)
        return _safe_response(success=True, status="recorded", asset=deepcopy(record), record=deepcopy(record), asset_id=record["asset_id"], storage_mode="dev_memory", dev_only=True, fallback_used=True)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO product_asset_records
                (asset_id, tenant_id, project_id, uploaded_by, asset_type, filename,
                 original_filename, mime_type, byte_size, checksum, storage_provider,
                 bucket, object_key, local_path, preview_url, download_url, preview_ready,
                 download_ready, status, approval_status, source_runtime, payload_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (asset_id)
                DO UPDATE SET
                    tenant_id = EXCLUDED.tenant_id,
                    project_id = EXCLUDED.project_id,
                    uploaded_by = EXCLUDED.uploaded_by,
                    asset_type = EXCLUDED.asset_type,
                    filename = EXCLUDED.filename,
                    original_filename = EXCLUDED.original_filename,
                    mime_type = EXCLUDED.mime_type,
                    byte_size = EXCLUDED.byte_size,
                    checksum = EXCLUDED.checksum,
                    storage_provider = EXCLUDED.storage_provider,
                    bucket = EXCLUDED.bucket,
                    object_key = EXCLUDED.object_key,
                    local_path = EXCLUDED.local_path,
                    preview_url = EXCLUDED.preview_url,
                    download_url = EXCLUDED.download_url,
                    preview_ready = EXCLUDED.preview_ready,
                    download_ready = EXCLUDED.download_ready,
                    status = EXCLUDED.status,
                    approval_status = EXCLUDED.approval_status,
                    source_runtime = EXCLUDED.source_runtime,
                    payload_json = EXCLUDED.payload_json,
                    updated_at = NOW(),
                    deleted_at = NULL,
                    credential_values_exposed = FALSE
                RETURNING asset_id, tenant_id, project_id, uploaded_by, asset_type,
                          filename, original_filename, mime_type, byte_size, checksum,
                          storage_provider, bucket, object_key, local_path, preview_url,
                          download_url, preview_ready, download_ready, status,
                          approval_status, source_runtime, payload_json, created_at,
                          updated_at, deleted_at, credential_values_exposed
                """,
                (
                    record["asset_id"], record["tenant_id"], record["project_id"], record["uploaded_by"],
                    record["asset_type"], record["filename"], record["original_filename"], record["mime_type"],
                    record["byte_size"], record["checksum"] or None, record["storage_provider"] or None,
                    record["bucket"] or None, record["object_key"] or None, record["local_path"] or None,
                    record["preview_url"] or None, record["download_url"] or None, record["preview_ready"],
                    record["download_ready"], record["status"], record["approval_status"], record["source_runtime"],
                    _json(record["payload"]),
                ),
            )
            row = cur.fetchone()
        conn.commit()
    item = _row(row, _asset_columns())
    return _safe_response(success=True, status="recorded", asset=item, record=item, asset_id=item["asset_id"], storage_mode="postgres", durable=True)


def get_product_asset(asset_id: str, tenant_id: str = "") -> Dict[str, Any]:
    readiness = ensure_product_asset_metadata_tables()
    if not readiness.get("success"):
        return readiness
    clean_id = _clean(asset_id)
    if _using_dev(readiness):
        item = deepcopy(_DEV_PRODUCT_ASSETS.get(clean_id))
        if not item or (tenant_id and item.get("tenant_id") != tenant_id) or item.get("deleted_at"):
            return _safe_response(success=False, status="not_found", asset_id=clean_id, storage_mode="dev_memory", dev_only=True, fallback_used=True)
        return _safe_response(success=True, status="found", asset=item, record=item, storage_mode="dev_memory", dev_only=True, fallback_used=True)

    clauses = ["asset_id = %s", "deleted_at IS NULL"]
    params: List[Any] = [clean_id]
    if tenant_id:
        clauses.append("tenant_id = %s")
        params.append(tenant_id)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {', '.join(_asset_columns())} FROM product_asset_records WHERE {' AND '.join(clauses)} LIMIT 1", params)
            row = cur.fetchone()
    if not row:
        return _safe_response(success=False, status="not_found", asset_id=clean_id, storage_mode="postgres", durable=True)
    item = _row(row, _asset_columns())
    return _safe_response(success=True, status="found", asset=item, record=item, storage_mode="postgres", durable=True)


def list_product_assets(
    *,
    tenant_id: str = "",
    project_id: str = "",
    asset_type: str = "",
    status: str = "",
    include_deleted: bool = False,
    limit: int = 100,
) -> Dict[str, Any]:
    readiness = ensure_product_asset_metadata_tables()
    if not readiness.get("success"):
        return readiness
    safe_limit = _limit(limit)
    if _using_dev(readiness):
        records = list(_DEV_PRODUCT_ASSETS.values())
        if not include_deleted:
            records = [item for item in records if not item.get("deleted_at")]
        if tenant_id:
            records = [item for item in records if item.get("tenant_id") == tenant_id]
        if project_id:
            records = [item for item in records if item.get("project_id") == project_id]
        if asset_type:
            records = [item for item in records if item.get("asset_type") == asset_type]
        if status:
            records = [item for item in records if item.get("status") == status]
        records = sorted(records, key=lambda item: str(item.get("created_at") or ""), reverse=True)[:safe_limit]
        return _safe_response(success=True, status="listed", count=len(records), asset_count=len(records), total_asset_count=len([item for item in _DEV_PRODUCT_ASSETS.values() if not item.get("deleted_at")]), assets=deepcopy(records), records=deepcopy(records), storage_mode="dev_memory", dev_only=True, fallback_used=True)

    clauses = []
    params: List[Any] = []
    if not include_deleted:
        clauses.append("deleted_at IS NULL")
    if tenant_id:
        clauses.append("tenant_id = %s")
        params.append(tenant_id)
    if project_id:
        clauses.append("project_id = %s")
        params.append(project_id)
    if asset_type:
        clauses.append("asset_type = %s")
        params.append(asset_type)
    if status:
        clauses.append("status = %s")
        params.append(status)
    where = " AND ".join(clauses) if clauses else "1 = 1"
    params.append(safe_limit)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {', '.join(_asset_columns())} FROM product_asset_records WHERE {where} ORDER BY created_at DESC LIMIT %s", params)
            rows = cur.fetchall()
            cur.execute("SELECT COUNT(*) FROM product_asset_records WHERE deleted_at IS NULL")
            total = cur.fetchone()[0]
    records = [_row(row, _asset_columns()) for row in rows]
    return _safe_response(success=True, status="listed", count=len(records), asset_count=len(records), total_asset_count=int(total or 0), assets=records, records=records, storage_mode="postgres", durable=True)


def update_product_asset_status(
    *,
    asset_id: str,
    tenant_id: str = "",
    status: str = "recorded",
    approval_status: str = "",
    actor_role: str = "system",
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    readiness = ensure_product_asset_metadata_tables()
    if not readiness.get("success"):
        return readiness
    clean_id = _clean(asset_id)
    if _using_dev(readiness):
        item = _DEV_PRODUCT_ASSETS.get(clean_id)
        if not item or (tenant_id and item.get("tenant_id") != tenant_id):
            return _safe_response(success=False, status="not_found", asset_id=clean_id, storage_mode="dev_memory", dev_only=True, fallback_used=True)
        item["status"] = _clean(status, item.get("status") or "recorded")
        if approval_status:
            item["approval_status"] = approval_status
        item["updated_at"] = _now_iso()
        record_product_asset_event(asset_id=clean_id, tenant_id=item["tenant_id"], project_id=item.get("project_id") or "default_project", event_type="product_asset_status_updated", actor_role=actor_role, payload=payload or {"status": item["status"], "approval_status": item.get("approval_status")})
        return _safe_response(success=True, status="updated", asset=deepcopy(item), record=deepcopy(item), storage_mode="dev_memory", dev_only=True, fallback_used=True)

    updates = ["status = %s", "updated_at = NOW()", "credential_values_exposed = FALSE"]
    params: List[Any] = [_clean(status, "recorded")]
    if approval_status:
        updates.append("approval_status = %s")
        params.append(approval_status)
    clauses = ["asset_id = %s", "deleted_at IS NULL"]
    params.append(clean_id)
    if tenant_id:
        clauses.append("tenant_id = %s")
        params.append(tenant_id)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                UPDATE product_asset_records
                SET {', '.join(updates)}
                WHERE {' AND '.join(clauses)}
                RETURNING {', '.join(_asset_columns())}
                """,
                params,
            )
            row = cur.fetchone()
        conn.commit()
    if not row:
        return _safe_response(success=False, status="not_found", asset_id=clean_id, storage_mode="postgres", durable=True)
    item = _row(row, _asset_columns())
    record_product_asset_event(asset_id=clean_id, tenant_id=item["tenant_id"], project_id=item.get("project_id") or "default_project", event_type="product_asset_status_updated", actor_role=actor_role, payload=payload or {"status": item["status"], "approval_status": item.get("approval_status")})
    return _safe_response(success=True, status="updated", asset=item, record=item, storage_mode="postgres", durable=True)


def delete_product_asset(
    *,
    asset_id: str,
    tenant_id: str = "",
    actor_role: str = "system",
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    readiness = ensure_product_asset_metadata_tables()
    if not readiness.get("success"):
        return readiness
    clean_id = _clean(asset_id)
    if _using_dev(readiness):
        item = _DEV_PRODUCT_ASSETS.get(clean_id)
        if not item or (tenant_id and item.get("tenant_id") != tenant_id) or item.get("deleted_at"):
            return _safe_response(success=False, status="not_found", asset_id=clean_id, storage_mode="dev_memory", dev_only=True, fallback_used=True)
        item["status"] = "deleted"
        item["deleted_at"] = _now_iso()
        item["updated_at"] = item["deleted_at"]
        item = _normalise_product_asset_record(item)
        _DEV_PRODUCT_ASSETS[clean_id] = deepcopy(item)
        record_product_asset_event(asset_id=clean_id, tenant_id=item["tenant_id"], project_id=item.get("project_id") or "default_project", event_type="product_asset_deleted", actor_role=actor_role, payload=payload or {})
        return _safe_response(success=True, status="deleted", asset_id=clean_id, asset=deepcopy(item), record=deepcopy(item), storage_mode="dev_memory", dev_only=True, fallback_used=True)

    clauses = ["asset_id = %s", "deleted_at IS NULL"]
    params: List[Any] = [clean_id]
    if tenant_id:
        clauses.append("tenant_id = %s")
        params.append(tenant_id)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                UPDATE product_asset_records
                SET status = 'deleted',
                    deleted_at = NOW(),
                    updated_at = NOW(),
                    preview_ready = FALSE,
                    download_ready = FALSE,
                    credential_values_exposed = FALSE
                WHERE {' AND '.join(clauses)}
                RETURNING {', '.join(_asset_columns())}
                """,
                params,
            )
            row = cur.fetchone()
        conn.commit()
    if not row:
        return _safe_response(success=False, status="not_found", asset_id=clean_id, storage_mode="postgres", durable=True)
    item = _row(row, _asset_columns())
    record_product_asset_event(asset_id=clean_id, tenant_id=item["tenant_id"], project_id=item.get("project_id") or "default_project", event_type="product_asset_deleted", actor_role=actor_role, payload=payload or {})
    return _safe_response(success=True, status="deleted", asset_id=clean_id, asset=item, record=item, storage_mode="postgres", durable=True)


def record_product_asset_event(
    *,
    asset_id: str = "",
    tenant_id: str,
    project_id: str = "default_project",
    event_type: str,
    actor_role: str = "",
    payload: Optional[Dict[str, Any]] = None,
    event_id: str = "",
) -> Dict[str, Any]:
    readiness = ensure_product_asset_metadata_tables()
    if not readiness.get("success"):
        return readiness
    event = {
        "event_id": _clean(event_id) or f"product_asset_event_{uuid.uuid4().hex[:16]}",
        "asset_id": _clean(asset_id),
        "tenant_id": _clean(tenant_id, "owner_admin"),
        "project_id": _clean(project_id, "default_project"),
        "event_type": _clean(event_type, "product_asset_event"),
        "actor_role": _clean(actor_role),
        "payload": _scrub_sensitive(payload or {}),
        "created_at": _now_iso(),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
    if _using_dev(readiness):
        _DEV_PRODUCT_ASSET_EVENTS[event["event_id"]] = deepcopy(event)
        return _safe_response(success=True, status="recorded", event=deepcopy(event), event_id=event["event_id"], storage_mode="dev_memory", dev_only=True, fallback_used=True)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO product_asset_events
                (event_id, asset_id, tenant_id, project_id, event_type, actor_role, payload_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
                RETURNING event_id, asset_id, tenant_id, project_id, event_type, actor_role, payload_json, created_at
                """,
                (event["event_id"], event["asset_id"] or None, event["tenant_id"], event["project_id"], event["event_type"], event["actor_role"] or None, _json(event["payload"])),
            )
            row = cur.fetchone()
        conn.commit()
    item = _row(row, _event_columns())
    return _safe_response(success=True, status="recorded", event=item, event_id=item["event_id"], storage_mode="postgres", durable=True)


def get_product_asset_metadata_summary(tenant_id: str = "") -> Dict[str, Any]:
    readiness = ensure_product_asset_metadata_tables()
    if not readiness.get("success"):
        return readiness
    assets = list_product_assets(tenant_id=tenant_id, limit=500)
    if _using_dev(readiness):
        events = list(_DEV_PRODUCT_ASSET_EVENTS.values())
        if tenant_id:
            events = [item for item in events if item.get("tenant_id") == tenant_id]
        event_count = len(events)
    else:
        clauses = []
        params: List[Any] = []
        if tenant_id:
            clauses.append("tenant_id = %s")
            params.append(tenant_id)
        where = " AND ".join(clauses) if clauses else "1 = 1"
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) FROM product_asset_events WHERE {where}", params)
                event_count = int(cur.fetchone()[0] or 0)
    return _safe_response(
        success=True,
        status="ready",
        product_asset_metadata_ready=True,
        storage_mode=readiness.get("storage_mode"),
        durable=readiness.get("durable", False),
        dev_only=readiness.get("dev_only", False),
        not_production_durable=readiness.get("not_production_durable", False),
        asset_count=assets.get("asset_count", 0),
        total_asset_count=assets.get("total_asset_count", 0),
        event_count=event_count,
        assets=assets.get("assets", [])[:20],
    )


def reset_dev_product_asset_metadata_for_tests() -> Dict[str, Any]:
    _DEV_PRODUCT_ASSETS.clear()
    _DEV_PRODUCT_ASSET_EVENTS.clear()
    return _safe_response(success=True, reset=True, status="dev_product_asset_metadata_reset", storage_mode="dev_memory", dev_only=True, not_production_durable=True, fallback_used=True)
