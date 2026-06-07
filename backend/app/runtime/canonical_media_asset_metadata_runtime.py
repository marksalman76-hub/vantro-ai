from __future__ import annotations

import json
import os
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


CANONICAL_MEDIA_ASSET_METADATA_PROFILE = "canonical_media_asset_metadata_runtime_v1"

_DEV_MEDIA_ASSETS: Dict[str, Dict[str, Any]] = {}
_DEV_DELIVERABLE_LINKS: Dict[str, Dict[str, Any]] = {}
_DEV_DELIVERY_PACKETS: Dict[str, Dict[str, Any]] = {}
_DEV_ACCESS_EVENTS: Dict[str, Dict[str, Any]] = {}


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
    timeout = max(1, min(int(os.getenv("MEDIA_METADATA_CONNECT_TIMEOUT_SECONDS") or 2), 10))
    return psycopg.connect(_database_url(), connect_timeout=timeout)


def _safe_response(**payload: Any) -> Dict[str, Any]:
    result = dict(payload)
    result.setdefault("canonical_media_asset_metadata_profile", CANONICAL_MEDIA_ASSET_METADATA_PROFILE)
    result.setdefault("authority", "backend_canonical")
    result.setdefault("production_fail_closed", False)
    result.setdefault("credential_values_exposed", False)
    result.setdefault("customer_safe", True)
    return result


def _unavailable(reason: str) -> Dict[str, Any]:
    return _safe_response(
        success=False,
        status="canonical_media_asset_metadata_store_unavailable",
        media_asset_metadata_ready=False,
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
    return str(value or default).strip()


def _limit(value: int, default: int = 50, maximum: int = 500) -> int:
    try:
        parsed = int(value or default)
    except Exception:
        parsed = default
    return max(1, min(parsed, maximum))


def _scrub_sensitive(data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    safe: Dict[str, Any] = {}
    for key, value in (data or {}).items():
        lowered = str(key).lower()
        if any(marker in lowered for marker in ("secret", "token", "api_key", "password", "credential")):
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


def _is_playable_reference(*values: Any) -> bool:
    for value in values:
        text = str(value or "").strip()
        if not text or text.startswith("data:"):
            continue
        if text.startswith(("http://", "https://")):
            return True
        lowered = text.lower()
        if "/runtime_outputs/" in lowered or "\\runtime_outputs\\" in lowered:
            return True
        if lowered.endswith((".mp4", ".mov", ".webm", ".mp3", ".wav", ".m4a", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".pdf")):
            return True
    return False


def _normalise_asset_record(record: Dict[str, Any]) -> Dict[str, Any]:
    playable = bool(
        record.get("playable")
        or _is_playable_reference(
            record.get("preview_url"),
            record.get("download_url"),
            record.get("provider_url"),
            record.get("local_path"),
        )
    )
    metadata_only = bool(record.get("metadata_only")) or not playable
    if metadata_only:
        playable = False

    preview_ready = bool(record.get("preview_ready")) and playable
    download_ready = bool(record.get("download_ready")) and playable

    return {
        **record,
        "playable": playable,
        "metadata_only": metadata_only,
        "preview_ready": preview_ready,
        "download_ready": download_ready,
        "credential_values_exposed": False,
        "customer_safe": True,
    }


def _asset_columns() -> List[str]:
    return [
        "asset_id",
        "tenant_id",
        "project_id",
        "execution_id",
        "provider_job_id",
        "provider_execution_id",
        "orchestration_id",
        "agent_id",
        "asset_type",
        "media_type",
        "status",
        "storage_provider",
        "bucket",
        "object_key",
        "local_path",
        "provider_url",
        "preview_url",
        "download_url",
        "mime_type",
        "byte_size",
        "checksum",
        "preview_ready",
        "download_ready",
        "playable",
        "metadata_only",
        "source_runtime",
        "payload_json",
        "created_at",
        "updated_at",
        "deleted_at",
        "credential_values_exposed",
    ]


def _link_columns() -> List[str]:
    return ["link_id", "tenant_id", "project_id", "execution_id", "deliverable_id", "asset_id", "link_type", "status", "created_at"]


def _packet_columns() -> List[str]:
    return [
        "delivery_packet_id",
        "tenant_id",
        "project_id",
        "asset_id",
        "delivery_status",
        "preview_ready",
        "download_ready",
        "signed_preview_url",
        "signed_download_url",
        "expires_at",
        "payload_json",
        "created_at",
    ]


def _event_columns() -> List[str]:
    return ["event_id", "tenant_id", "project_id", "asset_id", "event_type", "actor_role", "payload_json", "created_at"]


def _row(row: Any, columns: List[str]) -> Dict[str, Any]:
    result = dict(zip(columns, row))
    if "payload_json" in result:
        result["payload"] = _parse_json(result.pop("payload_json", None))
    for key, value in list(result.items()):
        result[key] = _dt(value)
    result["credential_values_exposed"] = False
    result["customer_safe"] = True
    return _normalise_asset_record(result) if "asset_id" in result and "source_runtime" in result else result


def ensure_media_asset_metadata_tables() -> Dict[str, Any]:
    if not _database_url():
        if _is_production():
            return _unavailable("DATABASE_URL_missing")
        return _safe_response(
            success=True,
            status="dev_only_media_asset_metadata_ready",
            media_asset_metadata_ready=True,
            durable=False,
            storage_mode="dev_memory",
            persistence_mode="dev_only",
            dev_only=True,
            not_production_durable=True,
            authority="backend_canonical",
        )

    if _psycopg() is None:
        if _is_production():
            return _unavailable("psycopg_unavailable")
        return _safe_response(
            success=True,
            status="dev_only_media_asset_metadata_ready",
            media_asset_metadata_ready=True,
            durable=False,
            storage_mode="dev_memory",
            persistence_mode="dev_only",
            dev_only=True,
            not_production_durable=True,
            postgres_configured_but_driver_unavailable=True,
            authority="backend_canonical",
        )

    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS media_asset_records (
                        asset_id TEXT PRIMARY KEY,
                        tenant_id TEXT NOT NULL,
                        project_id TEXT NOT NULL DEFAULT 'default_project',
                        execution_id TEXT,
                        provider_job_id TEXT,
                        provider_execution_id TEXT,
                        orchestration_id TEXT,
                        agent_id TEXT,
                        asset_type TEXT,
                        media_type TEXT,
                        status TEXT NOT NULL DEFAULT 'recorded',
                        storage_provider TEXT,
                        bucket TEXT,
                        object_key TEXT,
                        local_path TEXT,
                        provider_url TEXT,
                        preview_url TEXT,
                        download_url TEXT,
                        mime_type TEXT,
                        byte_size BIGINT,
                        checksum TEXT,
                        preview_ready BOOLEAN NOT NULL DEFAULT FALSE,
                        download_ready BOOLEAN NOT NULL DEFAULT FALSE,
                        playable BOOLEAN NOT NULL DEFAULT FALSE,
                        metadata_only BOOLEAN NOT NULL DEFAULT TRUE,
                        source_runtime TEXT,
                        payload_json JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        deleted_at TIMESTAMPTZ,
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_media_asset_records_tenant_created ON media_asset_records (tenant_id, created_at DESC)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_media_asset_records_execution ON media_asset_records (execution_id)")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS deliverable_asset_links (
                        link_id TEXT PRIMARY KEY,
                        tenant_id TEXT NOT NULL,
                        project_id TEXT NOT NULL DEFAULT 'default_project',
                        execution_id TEXT,
                        deliverable_id TEXT,
                        asset_id TEXT NOT NULL,
                        link_type TEXT NOT NULL DEFAULT 'deliverable_asset',
                        status TEXT NOT NULL DEFAULT 'linked',
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_deliverable_asset_links_deliverable ON deliverable_asset_links (tenant_id, deliverable_id, created_at DESC)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_deliverable_asset_links_asset ON deliverable_asset_links (asset_id)")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS asset_delivery_packets (
                        delivery_packet_id TEXT PRIMARY KEY,
                        tenant_id TEXT NOT NULL,
                        project_id TEXT NOT NULL DEFAULT 'default_project',
                        asset_id TEXT NOT NULL,
                        delivery_status TEXT NOT NULL DEFAULT 'ready',
                        preview_ready BOOLEAN NOT NULL DEFAULT FALSE,
                        download_ready BOOLEAN NOT NULL DEFAULT FALSE,
                        signed_preview_url TEXT,
                        signed_download_url TEXT,
                        expires_at TIMESTAMPTZ,
                        payload_json JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_asset_delivery_packets_asset_created ON asset_delivery_packets (asset_id, created_at DESC)")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS asset_access_events (
                        event_id TEXT PRIMARY KEY,
                        tenant_id TEXT NOT NULL,
                        project_id TEXT NOT NULL DEFAULT 'default_project',
                        asset_id TEXT,
                        event_type TEXT NOT NULL,
                        actor_role TEXT,
                        payload_json JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_asset_access_events_tenant_created ON asset_access_events (tenant_id, created_at DESC)")
            conn.commit()
        return _safe_response(success=True, status="media_asset_metadata_ready", media_asset_metadata_ready=True, durable=True, storage_mode="postgres", persistence_mode="postgres", dev_only=False, not_production_durable=False)
    except Exception as exc:
        if _is_production():
            return _unavailable(str(exc))
        return _safe_response(success=True, status="dev_only_media_asset_metadata_ready", media_asset_metadata_ready=True, durable=False, storage_mode="dev_memory", persistence_mode="dev_only", dev_only=True, not_production_durable=True, postgres_error=str(exc))


def record_media_asset(
    *,
    asset_id: str = "",
    tenant_id: str,
    project_id: str = "default_project",
    execution_id: str = "",
    provider_job_id: str = "",
    provider_execution_id: str = "",
    orchestration_id: str = "",
    agent_id: str = "",
    asset_type: str = "media",
    media_type: str = "",
    status: str = "recorded",
    storage_provider: str = "",
    bucket: str = "",
    object_key: str = "",
    local_path: str = "",
    provider_url: str = "",
    preview_url: str = "",
    download_url: str = "",
    mime_type: str = "",
    byte_size: Optional[int] = None,
    checksum: str = "",
    preview_ready: bool = False,
    download_ready: bool = False,
    playable: bool = False,
    metadata_only: Optional[bool] = None,
    source_runtime: str = "canonical_media_asset_metadata_runtime",
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    readiness = ensure_media_asset_metadata_tables()
    if not readiness.get("success"):
        return readiness

    record = _normalise_asset_record(
        {
            "asset_id": _clean(asset_id) or f"asset_{uuid.uuid4().hex[:16]}",
            "tenant_id": _clean(tenant_id, "tenant_unknown"),
            "project_id": _clean(project_id, "default_project"),
            "execution_id": _clean(execution_id),
            "provider_job_id": _clean(provider_job_id),
            "provider_execution_id": _clean(provider_execution_id),
            "orchestration_id": _clean(orchestration_id),
            "agent_id": _clean(agent_id),
            "asset_type": _clean(asset_type, "media"),
            "media_type": _clean(media_type) or _clean(asset_type, "media"),
            "status": _clean(status, "recorded"),
            "storage_provider": _clean(storage_provider),
            "bucket": _clean(bucket),
            "object_key": _clean(object_key),
            "local_path": _clean(local_path),
            "provider_url": _clean(provider_url),
            "preview_url": _clean(preview_url),
            "download_url": _clean(download_url),
            "mime_type": _clean(mime_type),
            "byte_size": int(byte_size) if byte_size is not None and str(byte_size).strip() else None,
            "checksum": _clean(checksum),
            "preview_ready": bool(preview_ready),
            "download_ready": bool(download_ready),
            "playable": bool(playable),
            "metadata_only": bool(metadata_only) if metadata_only is not None else False,
            "source_runtime": _clean(source_runtime, "canonical_media_asset_metadata_runtime"),
            "payload": _scrub_sensitive(payload or {}),
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
            "deleted_at": None,
            "credential_values_exposed": False,
            "customer_safe": True,
        }
    )

    if _using_dev(readiness):
        existing = _DEV_MEDIA_ASSETS.get(record["asset_id"], {})
        record["created_at"] = existing.get("created_at") or record["created_at"]
        _DEV_MEDIA_ASSETS[record["asset_id"]] = deepcopy(record)
        return _safe_response(success=True, status="recorded", asset=deepcopy(record), record=deepcopy(record), asset_id=record["asset_id"], storage_mode="dev_memory", dev_only=True)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO media_asset_records
                (asset_id, tenant_id, project_id, execution_id, provider_job_id, provider_execution_id,
                 orchestration_id, agent_id, asset_type, media_type, status, storage_provider,
                 bucket, object_key, local_path, provider_url, preview_url, download_url,
                 mime_type, byte_size, checksum, preview_ready, download_ready, playable,
                 metadata_only, source_runtime, payload_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (asset_id)
                DO UPDATE SET
                    tenant_id = EXCLUDED.tenant_id,
                    project_id = EXCLUDED.project_id,
                    execution_id = EXCLUDED.execution_id,
                    provider_job_id = EXCLUDED.provider_job_id,
                    provider_execution_id = EXCLUDED.provider_execution_id,
                    orchestration_id = EXCLUDED.orchestration_id,
                    agent_id = EXCLUDED.agent_id,
                    asset_type = EXCLUDED.asset_type,
                    media_type = EXCLUDED.media_type,
                    status = EXCLUDED.status,
                    storage_provider = EXCLUDED.storage_provider,
                    bucket = EXCLUDED.bucket,
                    object_key = EXCLUDED.object_key,
                    local_path = EXCLUDED.local_path,
                    provider_url = EXCLUDED.provider_url,
                    preview_url = EXCLUDED.preview_url,
                    download_url = EXCLUDED.download_url,
                    mime_type = EXCLUDED.mime_type,
                    byte_size = EXCLUDED.byte_size,
                    checksum = EXCLUDED.checksum,
                    preview_ready = EXCLUDED.preview_ready,
                    download_ready = EXCLUDED.download_ready,
                    playable = EXCLUDED.playable,
                    metadata_only = EXCLUDED.metadata_only,
                    source_runtime = EXCLUDED.source_runtime,
                    payload_json = EXCLUDED.payload_json,
                    updated_at = NOW(),
                    credential_values_exposed = FALSE
                RETURNING asset_id, tenant_id, project_id, execution_id, provider_job_id,
                          provider_execution_id, orchestration_id, agent_id, asset_type,
                          media_type, status, storage_provider, bucket, object_key,
                          local_path, provider_url, preview_url, download_url, mime_type,
                          byte_size, checksum, preview_ready, download_ready, playable,
                          metadata_only, source_runtime, payload_json, created_at,
                          updated_at, deleted_at, credential_values_exposed
                """,
                (
                    record["asset_id"], record["tenant_id"], record["project_id"], record["execution_id"] or None,
                    record["provider_job_id"] or None, record["provider_execution_id"] or None,
                    record["orchestration_id"] or None, record["agent_id"] or None, record["asset_type"],
                    record["media_type"], record["status"], record["storage_provider"] or None,
                    record["bucket"] or None, record["object_key"] or None, record["local_path"] or None,
                    record["provider_url"] or None, record["preview_url"] or None, record["download_url"] or None,
                    record["mime_type"] or None, record["byte_size"], record["checksum"] or None,
                    record["preview_ready"], record["download_ready"], record["playable"],
                    record["metadata_only"], record["source_runtime"], _json(record["payload"]),
                ),
            )
            row = cur.fetchone()
        conn.commit()
    item = _row(row, _asset_columns())
    return _safe_response(success=True, status="recorded", asset=item, record=item, asset_id=item["asset_id"], storage_mode="postgres", durable=True)


def get_media_asset(asset_id: str, tenant_id: str = "") -> Dict[str, Any]:
    readiness = ensure_media_asset_metadata_tables()
    if not readiness.get("success"):
        return readiness
    clean_id = _clean(asset_id)
    if _using_dev(readiness):
        item = deepcopy(_DEV_MEDIA_ASSETS.get(clean_id))
        if not item or (tenant_id and item.get("tenant_id") != tenant_id):
            return _safe_response(success=False, status="not_found", asset_id=clean_id, storage_mode="dev_memory", dev_only=True)
        return _safe_response(success=True, status="found", asset=item, record=item, storage_mode="dev_memory", dev_only=True)
    clauses = ["asset_id = %s", "deleted_at IS NULL"]
    params: List[Any] = [clean_id]
    if tenant_id:
        clauses.append("tenant_id = %s")
        params.append(tenant_id)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {', '.join(_asset_columns())} FROM media_asset_records WHERE {' AND '.join(clauses)} LIMIT 1", params)
            row = cur.fetchone()
    if not row:
        return _safe_response(success=False, status="not_found", asset_id=clean_id, storage_mode="postgres", durable=True)
    item = _row(row, _asset_columns())
    return _safe_response(success=True, status="found", asset=item, record=item, storage_mode="postgres", durable=True)


def list_media_assets(
    *,
    tenant_id: str = "",
    project_id: str = "",
    execution_id: str = "",
    asset_type: str = "",
    limit: int = 50,
) -> Dict[str, Any]:
    readiness = ensure_media_asset_metadata_tables()
    if not readiness.get("success"):
        return readiness
    safe_limit = _limit(limit)
    if _using_dev(readiness):
        records = list(_DEV_MEDIA_ASSETS.values())
        if tenant_id:
            records = [item for item in records if item.get("tenant_id") == tenant_id]
        if project_id:
            records = [item for item in records if item.get("project_id") == project_id]
        if execution_id:
            records = [item for item in records if item.get("execution_id") == execution_id]
        if asset_type:
            records = [item for item in records if item.get("asset_type") == asset_type or item.get("media_type") == asset_type]
        records = sorted(records, key=lambda item: str(item.get("created_at") or ""), reverse=True)[:safe_limit]
        return _safe_response(success=True, status="listed", count=len(records), asset_count=len(records), assets=deepcopy(records), records=deepcopy(records), storage_mode="dev_memory", dev_only=True)

    clauses = ["deleted_at IS NULL"]
    params: List[Any] = []
    if tenant_id:
        clauses.append("tenant_id = %s")
        params.append(tenant_id)
    if project_id:
        clauses.append("project_id = %s")
        params.append(project_id)
    if execution_id:
        clauses.append("execution_id = %s")
        params.append(execution_id)
    if asset_type:
        clauses.append("(asset_type = %s OR media_type = %s)")
        params.extend([asset_type, asset_type])
    params.append(safe_limit)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {', '.join(_asset_columns())} FROM media_asset_records WHERE {' AND '.join(clauses)} ORDER BY created_at DESC LIMIT %s", params)
            rows = cur.fetchall()
    records = [_row(row, _asset_columns()) for row in rows]
    return _safe_response(success=True, status="listed", count=len(records), asset_count=len(records), assets=records, records=records, storage_mode="postgres", durable=True)


def link_asset_to_deliverable(
    *,
    tenant_id: str,
    asset_id: str,
    project_id: str = "default_project",
    execution_id: str = "",
    deliverable_id: str = "",
    link_type: str = "deliverable_asset",
    status: str = "linked",
    link_id: str = "",
) -> Dict[str, Any]:
    readiness = ensure_media_asset_metadata_tables()
    if not readiness.get("success"):
        return readiness
    link = {
        "link_id": _clean(link_id) or f"deliverable_asset_link_{uuid.uuid4().hex[:16]}",
        "tenant_id": _clean(tenant_id, "tenant_unknown"),
        "project_id": _clean(project_id, "default_project"),
        "execution_id": _clean(execution_id),
        "deliverable_id": _clean(deliverable_id),
        "asset_id": _clean(asset_id),
        "link_type": _clean(link_type, "deliverable_asset"),
        "status": _clean(status, "linked"),
        "created_at": _now_iso(),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
    if _using_dev(readiness):
        _DEV_DELIVERABLE_LINKS[link["link_id"]] = deepcopy(link)
        return _safe_response(success=True, status="linked", link=deepcopy(link), link_id=link["link_id"], storage_mode="dev_memory", dev_only=True)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO deliverable_asset_links
                (link_id, tenant_id, project_id, execution_id, deliverable_id, asset_id, link_type, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING link_id, tenant_id, project_id, execution_id, deliverable_id, asset_id, link_type, status, created_at
                """,
                (link["link_id"], link["tenant_id"], link["project_id"], link["execution_id"] or None, link["deliverable_id"] or None, link["asset_id"], link["link_type"], link["status"]),
            )
            row = cur.fetchone()
        conn.commit()
    item = _row(row, _link_columns())
    return _safe_response(success=True, status="linked", link=item, link_id=item["link_id"], storage_mode="postgres", durable=True)


def list_deliverable_assets(
    *,
    tenant_id: str,
    deliverable_id: str = "",
    execution_id: str = "",
    project_id: str = "",
    limit: int = 50,
) -> Dict[str, Any]:
    readiness = ensure_media_asset_metadata_tables()
    if not readiness.get("success"):
        return readiness
    safe_limit = _limit(limit)
    if _using_dev(readiness):
        links = [item for item in _DEV_DELIVERABLE_LINKS.values() if item.get("tenant_id") == tenant_id]
        if deliverable_id:
            links = [item for item in links if item.get("deliverable_id") == deliverable_id]
        if execution_id:
            links = [item for item in links if item.get("execution_id") == execution_id]
        if project_id:
            links = [item for item in links if item.get("project_id") == project_id]
        links = sorted(links, key=lambda item: str(item.get("created_at") or ""), reverse=True)[:safe_limit]
        assets = [deepcopy(_DEV_MEDIA_ASSETS[item["asset_id"]]) for item in links if item.get("asset_id") in _DEV_MEDIA_ASSETS]
        return _safe_response(success=True, status="listed", count=len(assets), assets=assets, links=deepcopy(links), storage_mode="dev_memory", dev_only=True)

    clauses = ["l.tenant_id = %s"]
    params: List[Any] = [tenant_id]
    if deliverable_id:
        clauses.append("l.deliverable_id = %s")
        params.append(deliverable_id)
    if execution_id:
        clauses.append("l.execution_id = %s")
        params.append(execution_id)
    if project_id:
        clauses.append("l.project_id = %s")
        params.append(project_id)
    params.append(safe_limit)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT {', '.join('a.' + col for col in _asset_columns())}
                FROM deliverable_asset_links l
                JOIN media_asset_records a ON a.asset_id = l.asset_id
                WHERE {' AND '.join(clauses)} AND a.deleted_at IS NULL
                ORDER BY l.created_at DESC
                LIMIT %s
                """,
                params,
            )
            asset_rows = cur.fetchall()
    assets = [_row(row, _asset_columns()) for row in asset_rows]
    return _safe_response(success=True, status="listed", count=len(assets), assets=assets, storage_mode="postgres", durable=True)


def record_asset_delivery_packet(
    *,
    tenant_id: str,
    asset_id: str,
    project_id: str = "default_project",
    delivery_packet_id: str = "",
    delivery_status: str = "ready",
    preview_ready: bool = False,
    download_ready: bool = False,
    signed_preview_url: str = "",
    signed_download_url: str = "",
    expires_at: Any = None,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    readiness = ensure_media_asset_metadata_tables()
    if not readiness.get("success"):
        return readiness
    packet = {
        "delivery_packet_id": _clean(delivery_packet_id) or f"asset_delivery_packet_{uuid.uuid4().hex[:16]}",
        "tenant_id": _clean(tenant_id, "tenant_unknown"),
        "project_id": _clean(project_id, "default_project"),
        "asset_id": _clean(asset_id),
        "delivery_status": _clean(delivery_status, "ready"),
        "preview_ready": bool(preview_ready),
        "download_ready": bool(download_ready),
        "signed_preview_url": _clean(signed_preview_url),
        "signed_download_url": _clean(signed_download_url),
        "expires_at": expires_at,
        "payload": _scrub_sensitive(payload or {}),
        "created_at": _now_iso(),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
    if _using_dev(readiness):
        _DEV_DELIVERY_PACKETS[packet["delivery_packet_id"]] = deepcopy(packet)
        return _safe_response(success=True, status="recorded", delivery_packet=deepcopy(packet), packet=deepcopy(packet), delivery_packet_id=packet["delivery_packet_id"], storage_mode="dev_memory", dev_only=True)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO asset_delivery_packets
                (delivery_packet_id, tenant_id, project_id, asset_id, delivery_status,
                 preview_ready, download_ready, signed_preview_url, signed_download_url,
                 expires_at, payload_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                RETURNING delivery_packet_id, tenant_id, project_id, asset_id, delivery_status,
                          preview_ready, download_ready, signed_preview_url, signed_download_url,
                          expires_at, payload_json, created_at
                """,
                (packet["delivery_packet_id"], packet["tenant_id"], packet["project_id"], packet["asset_id"], packet["delivery_status"], packet["preview_ready"], packet["download_ready"], packet["signed_preview_url"] or None, packet["signed_download_url"] or None, packet["expires_at"], _json(packet["payload"])),
            )
            row = cur.fetchone()
        conn.commit()
    item = _row(row, _packet_columns())
    return _safe_response(success=True, status="recorded", delivery_packet=item, packet=item, delivery_packet_id=item["delivery_packet_id"], storage_mode="postgres", durable=True)


def list_asset_delivery_packets(*, tenant_id: str = "", asset_id: str = "", project_id: str = "", limit: int = 50) -> Dict[str, Any]:
    readiness = ensure_media_asset_metadata_tables()
    if not readiness.get("success"):
        return readiness
    safe_limit = _limit(limit)
    if _using_dev(readiness):
        packets = list(_DEV_DELIVERY_PACKETS.values())
        if tenant_id:
            packets = [item for item in packets if item.get("tenant_id") == tenant_id]
        if asset_id:
            packets = [item for item in packets if item.get("asset_id") == asset_id]
        if project_id:
            packets = [item for item in packets if item.get("project_id") == project_id]
        packets = sorted(packets, key=lambda item: str(item.get("created_at") or ""), reverse=True)[:safe_limit]
        return _safe_response(success=True, status="listed", count=len(packets), delivery_packets=deepcopy(packets), packets=deepcopy(packets), storage_mode="dev_memory", dev_only=True)
    clauses = ["1 = 1"]
    params: List[Any] = []
    if tenant_id:
        clauses.append("tenant_id = %s")
        params.append(tenant_id)
    if asset_id:
        clauses.append("asset_id = %s")
        params.append(asset_id)
    if project_id:
        clauses.append("project_id = %s")
        params.append(project_id)
    params.append(safe_limit)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {', '.join(_packet_columns())} FROM asset_delivery_packets WHERE {' AND '.join(clauses)} ORDER BY created_at DESC LIMIT %s", params)
            rows = cur.fetchall()
    packets = [_row(row, _packet_columns()) for row in rows]
    return _safe_response(success=True, status="listed", count=len(packets), delivery_packets=packets, packets=packets, storage_mode="postgres", durable=True)


def record_asset_access_event(
    *,
    tenant_id: str,
    event_type: str,
    project_id: str = "default_project",
    asset_id: str = "",
    actor_role: str = "",
    payload: Optional[Dict[str, Any]] = None,
    event_id: str = "",
) -> Dict[str, Any]:
    readiness = ensure_media_asset_metadata_tables()
    if not readiness.get("success"):
        return readiness
    event = {
        "event_id": _clean(event_id) or f"asset_access_event_{uuid.uuid4().hex[:16]}",
        "tenant_id": _clean(tenant_id, "tenant_unknown"),
        "project_id": _clean(project_id, "default_project"),
        "asset_id": _clean(asset_id),
        "event_type": _clean(event_type, "asset_access_event"),
        "actor_role": _clean(actor_role),
        "payload": _scrub_sensitive(payload or {}),
        "created_at": _now_iso(),
        "credential_values_exposed": False,
        "customer_safe": True,
    }
    if _using_dev(readiness):
        _DEV_ACCESS_EVENTS[event["event_id"]] = deepcopy(event)
        return _safe_response(success=True, status="recorded", event=deepcopy(event), event_id=event["event_id"], storage_mode="dev_memory", dev_only=True)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO asset_access_events
                (event_id, tenant_id, project_id, asset_id, event_type, actor_role, payload_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
                RETURNING event_id, tenant_id, project_id, asset_id, event_type, actor_role, payload_json, created_at
                """,
                (event["event_id"], event["tenant_id"], event["project_id"], event["asset_id"] or None, event["event_type"], event["actor_role"] or None, _json(event["payload"])),
            )
            row = cur.fetchone()
        conn.commit()
    item = _row(row, _event_columns())
    return _safe_response(success=True, status="recorded", event=item, event_id=item["event_id"], storage_mode="postgres", durable=True)


def get_media_asset_metadata_summary(tenant_id: str = "") -> Dict[str, Any]:
    readiness = ensure_media_asset_metadata_tables()
    if not readiness.get("success"):
        return readiness
    assets = list_media_assets(tenant_id=tenant_id, limit=500)
    packets = list_asset_delivery_packets(tenant_id=tenant_id, limit=500)
    return _safe_response(
        success=True,
        status="ready",
        media_asset_metadata_ready=True,
        storage_mode=readiness.get("storage_mode"),
        durable=readiness.get("durable", False),
        dev_only=readiness.get("dev_only", False),
        not_production_durable=readiness.get("not_production_durable", False),
        asset_count=assets.get("asset_count", 0),
        delivery_packet_count=packets.get("count", 0),
        assets=assets.get("assets", [])[:20],
    )


def reset_dev_media_asset_metadata_for_tests() -> Dict[str, Any]:
    _DEV_MEDIA_ASSETS.clear()
    _DEV_DELIVERABLE_LINKS.clear()
    _DEV_DELIVERY_PACKETS.clear()
    _DEV_ACCESS_EVENTS.clear()
    return _safe_response(success=True, reset=True, status="dev_media_asset_metadata_reset", storage_mode="dev_memory", dev_only=True, not_production_durable=True)
