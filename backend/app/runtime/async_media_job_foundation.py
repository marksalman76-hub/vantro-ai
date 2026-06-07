
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4
import json
import threading

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT / "runtime_outputs" / "media_jobs"
STORE.mkdir(parents=True, exist_ok=True)

_LOCK = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _job_path(job_id: str) -> Path:
    return STORE / f"{job_id}.json"


def _scrub_sensitive(value: Any) -> Any:
    if isinstance(value, list):
        return [_scrub_sensitive(item) for item in value]
    if not isinstance(value, dict):
        return value
    safe: Dict[str, Any] = {}
    for key, item in value.items():
        lowered = str(key).lower()
        if any(marker in lowered for marker in ("token", "secret", "password", "api_key", "authorization", "credential", "debug", "raw")):
            continue
        safe[str(key)] = _scrub_sensitive(item)
    safe["credential_values_exposed"] = False
    return safe


def enqueue_media_job(*, task: str, agent_id: str, tenant_id: str, include_image: bool = True, include_audio: bool = True, include_video: bool = True, include_avatar: bool = False) -> Dict[str, Any]:
    job_id = f"media_job_{uuid4().hex[:12]}"
    job = {
        "success": True,
        "job_id": job_id,
        "status": "queued",
        "task": task,
        "agent_id": agent_id,
        "tenant_id": tenant_id,
        "include_image": include_image,
        "include_audio": include_audio,
        "include_video": include_video,
        "include_avatar": include_avatar,
        "lifecycle": "queued",
        "media_asset_count": 0,
        "real_media_asset_count": 0,
        "persisted_asset_count": 0,
        "preview_ready_count": 0,
        "download_ready_count": 0,
        "final_asset_ids": [],
        "final_assets": [],
        "created_at": _now(),
        "updated_at": _now(),
        "credential_values_exposed": False,
    }
    with _LOCK:
        _job_path(job_id).write_text(json.dumps(job, indent=2), encoding="utf-8")
    return job


def read_media_job(job_id: str) -> Dict[str, Any]:
    path = _job_path(job_id)
    if not path.exists():
        return {"success": False, "job_id": job_id, "status": "not_found", "credential_values_exposed": False}
    job = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(job, dict):
        job["credential_values_exposed"] = False
    return _scrub_sensitive(job)


def list_media_jobs(limit: int = 50) -> Dict[str, Any]:
    jobs = []
    for path in sorted(STORE.glob("media_job_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
        try:
            jobs.append(_scrub_sensitive(json.loads(path.read_text(encoding="utf-8"))))
        except Exception:
            continue
    return {
        "success": True,
        "status": "ready",
        "job_count": len(jobs),
        "jobs": jobs,
        "credential_values_exposed": False,
    }


def _write_job(job: Dict[str, Any]) -> None:
    _job_path(str(job["job_id"])).write_text(json.dumps(job, indent=2), encoding="utf-8")


def _label(value: Any, fallback: str = "") -> str:
    text = str(value or fallback).strip()
    if not text:
        return fallback
    return " ".join(part.capitalize() for part in text.replace("_", " ").split())


def _safe_blocked_reason(job: Dict[str, Any]) -> str:
    raw = str(job.get("error") or job.get("blocked_reason") or "").strip()
    if raw:
        lowered = raw.lower()
        if any(marker in lowered for marker in ("token", "secret", "password", "api_key", "authorization", "credential")):
            return "Provider execution is not configured for this media job. Connect the required provider credentials or run it again once provider dispatch is ready."
        if raw in {"no_playable_or_metadata_asset_result", "no_playable_provider_asset_result"}:
            return "Provider execution did not return a playable media asset. Connect or enable a supported media provider, then rerun the media job."
        return raw[:260]
    status = str(job.get("status") or "").lower()
    if status == "queued":
        return "Media generation is queued and waiting for delegated workforce processing."
    if status in {"processing", "running"}:
        return "Media generation is running. Refresh assets shortly."
    if status in {"failed", "blocked"}:
        return "Provider execution could not complete. Check provider readiness and rerun the media job."
    return "Media job evidence is available, but no playable generated asset is attached yet."


def media_job_to_visible_asset_evidence(job: Dict[str, Any], *, audience: str = "admin") -> Dict[str, Any]:
    job_id = str(job.get("job_id") or job.get("media_job_id") or "").strip()
    status = str(job.get("status") or job.get("media_job_status") or "queued").strip()
    agent_id = str(job.get("agent_id") or job.get("requested_agent") or "creative_media_agent").strip()
    final_assets = [asset for asset in job.get("final_assets", []) if isinstance(asset, dict)]
    playable_count = sum(1 for asset in final_assets if asset.get("playable") or asset.get("preview_ready"))
    generated_count = int(job.get("media_asset_count") or job.get("real_media_asset_count") or len(final_assets) or 0)
    blocked_reason = _safe_blocked_reason(job)
    provider_readiness = "ready" if playable_count else ("blocked" if status.lower() in {"failed", "blocked"} else status.lower() or "queued")
    preview_ready = any(asset.get("preview_ready") for asset in final_assets)
    download_ready = any(asset.get("download_ready") for asset in final_assets)
    title = f"Creative media job {_label(status, 'Queued').lower()}"

    return {
        "asset_id": job_id,
        "id": job_id,
        "job_id": job_id,
        "media_job_id": job_id,
        "task_id": job_id,
        "tenant_id": job.get("tenant_id") or "owner_admin",
        "agent_id": agent_id,
        "agent_label": _label(agent_id, "Creative Media Agent"),
        "provider": "creative_media_queue",
        "provider_key": "creative_media_queue",
        "provider_readiness": provider_readiness,
        "asset_type": "creative_media_job_evidence",
        "media_type": "creative_media_job_evidence",
        "title": title,
        "test_label": f"{title}: {_label(agent_id, 'Creative Media Agent')}",
        "file_name": job_id,
        "status": status,
        "delivery_status": "final_asset_ready" if playable_count else provider_readiness,
        "lifecycle_status": "preview_ready" if playable_count else "pending",
        "summary": (
            f"Creative media job {job_id} is {_label(status, 'queued').lower()}. "
            f"Generated assets: {generated_count}. Playable assets: {playable_count}."
        ),
        "blocked_reason": "" if playable_count else blocked_reason,
        "not_playable_reason": "" if playable_count else blocked_reason,
        "preview_ready": bool(preview_ready),
        "download_ready": bool(download_ready),
        "playable": bool(playable_count),
        "metadata_only": not bool(playable_count),
        "media_asset_count": generated_count,
        "real_media_asset_count": int(job.get("real_media_asset_count") or 0),
        "playable_asset_count": playable_count,
        "final_assets": final_assets if audience == "admin" else [],
        "owner_approval_required": False,
        "governed": True,
        "customer_safe": True,
        "client_safe": True,
        "credential_values_exposed": False,
        "created_at": job.get("created_at"),
        "updated_at": job.get("updated_at"),
    }


def _asset_delivery_summary(asset: Dict[str, Any]) -> Dict[str, Any]:
    persistence = asset.get("persistence") if isinstance(asset.get("persistence"), dict) else {}
    return {
        "asset_id": persistence.get("asset_id") or asset.get("asset_id"),
        "media_type": asset.get("media_type") or asset.get("asset_type"),
        "asset_type": asset.get("asset_type") or asset.get("media_type"),
        "status": asset.get("status"),
        "preview_ready": bool(persistence.get("preview_ready") or asset.get("preview_ready")),
        "download_ready": bool(persistence.get("download_ready") or asset.get("download_ready")),
        "playable": bool(persistence.get("playable") or asset.get("playable")),
        "storage_provider": persistence.get("storage_provider"),
    }


def process_media_job(job: Dict[str, Any]) -> Dict[str, Any]:
    job_id = str(job.get("job_id") or "")
    if not job_id:
        return {
            "success": False,
            "processed": False,
            "status": "invalid_job",
            "error": "missing_job_id",
            "credential_values_exposed": False,
        }

    try:
        with _LOCK:
            current = read_media_job(job_id)
            current_status = str(current.get("status") or "").lower()
            if current_status in {"processing", "completed", "blocked"}:
                return {
                    "success": True,
                    "processed": False,
                    "status": current_status,
                    "reason": "job_not_queued",
                    "job": current,
                    "credential_values_exposed": False,
                }
            job = current if current.get("success", True) is not False else job
            job["status"] = "processing"
            job["lifecycle"] = "processing"
            job["started_at"] = job.get("started_at") or _now()
            job["updated_at"] = _now()
            _write_job(job)

        from backend.app.runtime.shared_creative_media_generation_runtime import generate_creative_media_pack

        media_pack = generate_creative_media_pack(
            task=job.get("task") or "Create a premium creative media asset.",
            agent_id=job.get("agent_id") or "creative_agent",
            tenant_id=job.get("tenant_id") or "owner_admin",
            include_image=bool(job.get("include_image")),
            include_audio=bool(job.get("include_audio")),
            include_video=bool(job.get("include_video")),
            include_avatar=bool(job.get("include_avatar")),
        )

        final_assets = [
            _asset_delivery_summary(asset)
            for asset in media_pack.get("media_assets", [])
            if isinstance(asset, dict)
        ]
        playable_assets = [asset for asset in final_assets if asset.get("playable") or asset.get("preview_ready") or asset.get("download_ready")]

        if not playable_assets:
            job["status"] = "blocked"
            job["lifecycle"] = "provider_unavailable_or_no_playable_asset"
            job["blocked_reason"] = "Provider execution did not return a playable media asset. Connect or enable a supported media provider, then rerun the media job."
            job["media_pack_id"] = media_pack.get("media_pack_id")
            job["media_asset_count"] = len(media_pack.get("media_assets", []))
            job["real_media_asset_count"] = media_pack.get("real_media_asset_count", 0)
            job["persisted_asset_count"] = media_pack.get("persisted_asset_count", 0)
            job["final_asset_ids"] = [
                asset.get("asset_id")
                for asset in final_assets
                if asset.get("asset_id")
            ]
            job["final_assets"] = final_assets
            job["preview_ready_count"] = 0
            job["download_ready_count"] = 0
            job["blocked_at"] = _now()
            job["updated_at"] = _now()
            job["credential_values_exposed"] = False
            _write_job(job)
            return {
                "success": True,
                "processed": True,
                "status": "blocked",
                "job": job,
                "blocked_reason": job["blocked_reason"],
                "credential_values_exposed": False,
            }

        job["status"] = "completed"
        job["lifecycle"] = "final_asset_ready"
        job["media_pack_id"] = media_pack.get("media_pack_id")
        job["media_asset_count"] = len(media_pack.get("media_assets", []))
        job["real_media_asset_count"] = media_pack.get("real_media_asset_count", 0)
        job["persisted_asset_count"] = media_pack.get("persisted_asset_count", 0)
        job["final_asset_ids"] = [
            asset.get("asset_id")
            for asset in final_assets
            if asset.get("asset_id")
        ]
        job["final_assets"] = final_assets
        job["preview_ready_count"] = sum(1 for asset in playable_assets if asset.get("preview_ready"))
        job["download_ready_count"] = sum(1 for asset in playable_assets if asset.get("download_ready"))
        job["completed_at"] = _now()
        job["updated_at"] = _now()
        job["credential_values_exposed"] = False
        _write_job(job)

        return {"success": True, "processed": True, "job": job, "credential_values_exposed": False}
    except Exception as exc:
        job["status"] = "blocked"
        job["lifecycle"] = "provider_dispatch_blocked"
        job["blocked_reason"] = "Provider execution is not configured or could not complete safely. Connect the required media provider and rerun the job."
        job["blocked_at"] = _now()
        job["updated_at"] = _now()
        job["credential_values_exposed"] = False
        _write_job(job)
        return {
            "success": True,
            "processed": True,
            "status": "blocked",
            "job": job,
            "blocked_reason": job["blocked_reason"],
            "credential_values_exposed": False,
        }


def run_next_media_job() -> Dict[str, Any]:
    queued = [j for j in list_media_jobs(200).get("jobs", []) if j.get("status") == "queued"]
    if not queued:
        return {"success": True, "status": "empty", "processed": False}

    job = queued[-1]
    return process_media_job(job)


def run_all_media_jobs(limit: int = 25) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    processed = 0

    for _ in range(max(int(limit or 25), 1)):
        result = run_next_media_job()
        results.append(result)
        if not result.get("processed"):
            break
        processed += 1
        if result.get("success") is False:
            break

    return {
        "success": True,
        "status": "completed" if processed else "empty",
        "processed_count": processed,
        "results": results,
        "credential_values_exposed": False,
    }
