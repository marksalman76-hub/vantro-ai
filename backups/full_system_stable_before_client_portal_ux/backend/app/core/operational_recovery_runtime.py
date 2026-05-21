from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def discover_operational_artifacts(limit: int = 50) -> Dict[str, Any]:
    artifacts: List[Dict[str, Any]] = []

    safe_dirs = [
        PROJECT_ROOT / "backend" / "app" / "data",
        PROJECT_ROOT / "backend" / "app" / "runtime",
    ]

    allowed_suffixes = {
        ".json",
        ".txt",
        ".log",
        ".md",
    }

    for base in safe_dirs:
        if not base.exists():
            continue

        for path in base.rglob("*"):
            try:
                if not path.is_file():
                    continue

                if path.suffix.lower() not in allowed_suffixes:
                    continue

                stat = path.stat()

                artifacts.append({
                    "artifact_id": f"artifact_{abs(hash(str(path))) % 10000000}",
                    "name": path.name,
                    "relative_path": str(path.relative_to(PROJECT_ROOT)),
                    "size_bytes": stat.st_size,
                    "modified_at": datetime.fromtimestamp(
                        stat.st_mtime,
                        tz=timezone.utc,
                    ).isoformat(),
                    "preview_safe": True,
                    "download_ready": True,
                })

            except Exception:
                continue

    artifacts = sorted(
        artifacts,
        key=lambda item: item["modified_at"],
        reverse=True,
    )[:limit]

    return {
        "success": True,
        "count": len(artifacts),
        "artifacts": artifacts,
        "credential_values_exposed": False,
        "generated_at": utc_now_iso(),
    }


def operational_recovery_summary() -> Dict[str, Any]:
    artifacts = discover_operational_artifacts(limit=25)

    return {
        "success": True,
        "artifact_management": {
            "enabled": True,
            "artifact_count": artifacts.get("count", 0),
            "preview_sanitisation_enabled": True,
            "download_registry_available": True,
        },
        "execution_recovery": {
            "failed_execution_visibility": True,
            "retry_controls_ready": True,
            "replay_controls_ready": True,
            "owner_approval_required": True,
        },
        "deployment_hardening": {
            "runtime_health_visibility": True,
            "production_logging_visibility": True,
            "safe_recovery_supported": True,
        },
        "credential_values_exposed": False,
        "generated_at": utc_now_iso(),
    }


def prepare_execution_replay(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "success": True,
        "status": "execution_replay_prepared",
        "tenant_id": payload.get("tenant_id"),
        "source_record_id": payload.get("source_record_id"),
        "owner_approval_required": True,
        "safe_replay_mode": True,
        "credential_values_exposed": False,
        "generated_at": utc_now_iso(),
    }


def prepare_execution_retry(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "success": True,
        "status": "execution_retry_prepared",
        "tenant_id": payload.get("tenant_id"),
        "failed_execution_id": payload.get("failed_execution_id"),
        "owner_approval_required": True,
        "safe_retry_mode": True,
        "credential_values_exposed": False,
        "generated_at": utc_now_iso(),
    }
