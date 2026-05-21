"""
Provider Execution Audit Log

Persistent audit layer for LLM routing, provider readiness, and governed
live-call decisions.

Security:
- does not store provider credentials
- does not store internal prompts
- does not store backend configuration
- does not expose learning internals
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List
import json
import uuid


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
AUDIT_FILE = DATA_DIR / "provider_execution_audit_log.jsonl"


class ProviderExecutionAuditLog:
    def record(self, event: Dict[str, object]) -> Dict[str, object]:
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        safe_event = self._safe_event(event)

        record = {
            "audit_id": f"provider_audit_{uuid.uuid4().hex[:16]}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            **safe_event,
        }

        with AUDIT_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        return {
            "success": True,
            "audit_id": record["audit_id"],
            "stored": True,
            "credential_values_stored": False,
            "internal_prompts_stored": False,
            "backend_config_stored": False,
        }

    def latest(self, limit: int = 20) -> Dict[str, object]:
        if not AUDIT_FILE.exists():
            return {
                "success": True,
                "events": [],
                "count": 0,
            }

        lines = AUDIT_FILE.read_text(encoding="utf-8").splitlines()
        selected = lines[-limit:]

        events: List[Dict[str, object]] = []
        for line in selected:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

        return {
            "success": True,
            "events": events,
            "count": len(events),
        }

    def _safe_event(self, event: Dict[str, object]) -> Dict[str, object]:
        blocked_keys = {
            "prompt",
            "system_prompt",
            "developer_prompt",
            "internal_prompt",
            "api_key",
            "secret",
            "credential",
            "credentials",
            "provider_secret",
            "backend_config",
            "learning_rules",
            "memory_internals",
        }

        safe: Dict[str, object] = {}

        for key, value in event.items():
            lowered = key.lower()

            if lowered in blocked_keys:
                safe[f"{key}_blocked"] = True
                continue

            if isinstance(value, dict):
                safe[key] = self._safe_event(value)
                continue

            if isinstance(value, list):
                safe[key] = [
                    self._safe_event(item) if isinstance(item, dict) else item
                    for item in value
                ]
                continue

            safe[key] = value

        safe["client_safe"] = True
        safe["credential_values_stored"] = False
        safe["internal_prompts_stored"] = False
        safe["backend_config_stored"] = False

        return safe


provider_execution_audit_log = ProviderExecutionAuditLog()
