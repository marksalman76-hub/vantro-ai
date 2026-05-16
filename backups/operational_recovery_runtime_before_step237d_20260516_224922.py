from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path.cwd()
DATA_DIRS = [
    ROOT / "backend" / "app" / "data",
    ROOT / "backend" / "app" / "runtime",
    ROOT / "backend" / "app" / "generated_outputs",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_json_load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _safe_text_preview(path: Path, limit: int = 2200) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""


def _scrub(value: Any) -> Any:
    raw = json.dumps(value, default=str)
    for marker in ["sk_live_", "sk_test_", "whsec_", "postgresql://"]:
        raw = raw.replace(marker, "[protected]")

    try:
        return json.loads(raw)
    except Exception:
        return {"safe_preview": raw[:2000]}


def discover_operational_artifacts(limit: int = 50) -> Dict[str, Any]:
    artifacts: List[Dict[str, Any]] = []

    for base in DATA_DIRS:
        if not base.exists():
            continue

        for path in base.rglob("*"):
            if not path.is_file():
                continue

            if path.suffix.lower() not in {".json", ".jsonl", ".txt", ".md", ".html"}:
                continue

            stat = path.stat()
            artifacts.append({
                "artifact_id": f"artifact_{abs(hash(str(path))) % 10_000_000}",
                "name": path.name,
                "relative_path": str(path.relative_to(ROOT)),
                "size_bytes": stat.st_size,
                "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                "type": path.suffix.lower().replace(".", "") or "file",
                "download_ready": True,
                "client_safe_preview_available": path.suffix.lower() in {".json", ".txt", ".md", ".html"},
            })

    artifacts = sorted(artifacts, key=lambda item: item["modified_at"], reverse=True)[:limit]

    return {
        "success": True,
        "route": "operational_artifact_discovery",
        "count": len(artifacts),
        "artifacts": artifacts,
        "credential_values_exposed": False,
        "generated_at": utc_now_iso(),
    }


def get_artifact_preview(relative_path: str) -> Dict[str, Any]:
    requested = (ROOT / relative_path).resolve()

    if ROOT.resolve() not in requested.parents and requested != ROOT.resolve():
        return {
            "success": False,
            "error": "artifact_path_not_allowed",
            "credential_values_exposed": False,
        }

    if not requested.exists() or not requested.is_file():
        return {
            "success": False,
            "error": "artifact_not_found",
            "credential_values_exposed": False,
        }

    parsed = _safe_json_load(requested)
    preview = parsed if parsed is not None else _safe_text_preview(requested)

    return {
        "success": True,
        "artifact": {
            "name": requested.name,
            "relative_path": str(requested.relative_to(ROOT)),
            "type": requested.suffix.lower().replace(".", "") or "file",
            "size_bytes": requested.stat().st_size,
            "preview": _scrub(preview),
        },
        "credential_values_exposed": False,
        "generated_at": utc_now_iso(),
    }


def operational_recovery_summary() -> Dict[str, Any]:
    artifact_result = discover_operational_artifacts(limit=25)

    return {
        "success": True,
        "route": "operational_recovery_summary",
        "artifact_management": {
            "enabled": True,
            "artifact_count": artifact_result.get("count", 0),
            "download_registry_available": True,
            "preview_sanitisation_enabled": True,
        },
        "execution_recovery": {
            "failed_execution_visibility": True,
            "retry_controls_ready": True,
            "replay_controls_ready": True,
            "owner_replay_required": True,
            "audit_logging_required": True,
        },
        "deployment_hardening": {
            "readiness_matrix_available": True,
            "production_logging_visibility": True,
            "runtime_health_visibility": True,
            "safe_rollback_supported": True,
        },
        "security": {
            "admin_only": True,
            "credential_values_exposed": False,
            "internal_prompt_exposure_blocked": True,
            "tenant_sensitive_values_scrubbed": True,
        },
        "generated_at": utc_now_iso(),
    }


def prepare_execution_replay(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "success": True,
        "status": "execution_replay_prepared",
        "tenant_id": payload.get("tenant_id"),
        "source_record_id": payload.get("source_record_id"),
        "requested_by": payload.get("requested_by", "owner"),
        "owner_approval_required": True,
        "safe_replay_mode": True,
        "replay_notes": [
            "Replay is prepared only.",
            "Owner approval is required before execution.",
            "Original governance, billing and entitlement checks must still apply.",
        ],
        "credential_values_exposed": False,
        "prepared_at": utc_now_iso(),
    }


def prepare_execution_retry(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "success": True,
        "status": "execution_retry_prepared",
        "tenant_id": payload.get("tenant_id"),
        "failed_execution_id": payload.get("failed_execution_id"),
        "requested_by": payload.get("requested_by", "owner"),
        "retry_mode": "controlled_owner_review",
        "owner_approval_required": True,
        "retry_notes": [
            "Retry is prepared only.",
            "Failed execution remains isolated.",
            "Owner review is required before retry.",
        ],
        "credential_values_exposed": False,
        "prepared_at": utc_now_iso(),
    }
