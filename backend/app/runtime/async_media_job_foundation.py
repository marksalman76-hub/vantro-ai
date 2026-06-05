
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
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
        return {"success": False, "job_id": job_id, "status": "not_found"}
    return json.loads(path.read_text(encoding="utf-8"))


def list_media_jobs(limit: int = 50) -> Dict[str, Any]:
    jobs = []
    for path in sorted(STORE.glob("media_job_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
        try:
            jobs.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            continue
    return {
        "success": True,
        "status": "ready",
        "job_count": len(jobs),
        "jobs": jobs,
        "credential_values_exposed": False,
    }


def run_next_media_job() -> Dict[str, Any]:
    queued = [j for j in list_media_jobs(200).get("jobs", []) if j.get("status") == "queued"]
    if not queued:
        return {"success": True, "status": "empty", "processed": False}

    job = queued[-1]
    job_id = job["job_id"]

    try:
        job["status"] = "processing"
        job["updated_at"] = _now()
        _job_path(job_id).write_text(json.dumps(job, indent=2), encoding="utf-8")

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

        job["status"] = "completed"
        job["media_pack_id"] = media_pack.get("media_pack_id")
        job["media_asset_count"] = len(media_pack.get("media_assets", []))
        job["real_media_asset_count"] = media_pack.get("real_media_asset_count", 0)
        job["persisted_asset_count"] = media_pack.get("persisted_asset_count", 0)
        job["final_assets"] = [
            {
                "asset_id": asset.get("asset_id"),
                "media_type": asset.get("media_type"),
                "status": asset.get("status"),
                "preview_ready": asset.get("preview_ready"),
                "download_ready": asset.get("download_ready"),
            }
            for asset in media_pack.get("media_assets", [])
            if isinstance(asset, dict)
        ]
        job["updated_at"] = _now()
        _job_path(job_id).write_text(json.dumps(job, indent=2), encoding="utf-8")

        return {"success": True, "processed": True, "job": job, "credential_values_exposed": False}
    except Exception as exc:
        job["status"] = "failed"
        job["error"] = str(exc)[:800]
        job["updated_at"] = _now()
        _job_path(job_id).write_text(json.dumps(job, indent=2), encoding="utf-8")
        return {"success": False, "processed": True, "job": job, "error": str(exc)[:800], "credential_values_exposed": False}
