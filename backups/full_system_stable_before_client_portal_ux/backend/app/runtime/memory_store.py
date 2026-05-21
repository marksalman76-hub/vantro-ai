"""
Memory Store

Lightweight persistent memory layer for tenants, projects, agent outputs,
execution history, provider routing, and future optimisation signals.

This starts with JSON file persistence so the SaaS runtime can remember
client/project state before we move to SQLite/Postgres.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import json
import uuid


DATA_DIR = Path("backend/app/data")
MEMORY_FILE = DATA_DIR / "memory_store.json"


@dataclass
class MemoryRecord:
    memory_id: str
    tenant_id: str
    project_id: str
    record_type: str
    title: str
    payload: Dict[str, object]
    created_at: str


class MemoryStore:
    def __init__(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not MEMORY_FILE.exists():
            MEMORY_FILE.write_text("[]", encoding="utf-8")

    def add_record(
        self,
        tenant_id: str,
        project_id: str,
        record_type: str,
        title: str,
        payload: Dict[str, object],
    ) -> MemoryRecord:
        record = MemoryRecord(
            memory_id=f"mem_{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            project_id=project_id,
            record_type=record_type,
            title=title,
            payload=payload,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        records = self._load_records()
        records.append(asdict(record))
        self._save_records(records)

        return record

    def list_records(
        self,
        tenant_id: Optional[str] = None,
        project_id: Optional[str] = None,
        record_type: Optional[str] = None,
    ) -> List[Dict[str, object]]:
        records = self._load_records()

        if tenant_id:
            records = [record for record in records if record.get("tenant_id") == tenant_id]

        if project_id:
            records = [record for record in records if record.get("project_id") == project_id]

        if record_type:
            records = [record for record in records if record.get("record_type") == record_type]

        return records

    def latest_record(
        self,
        tenant_id: str,
        project_id: str,
        record_type: str,
    ) -> Optional[Dict[str, object]]:
        records = self.list_records(
            tenant_id=tenant_id,
            project_id=project_id,
            record_type=record_type,
        )

        if not records:
            return None

        return sorted(records, key=lambda record: str(record.get("created_at", "")))[-1]

    def _load_records(self) -> List[Dict[str, object]]:
        try:
            return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []

    def _save_records(self, records: List[Dict[str, object]]) -> None:
        MEMORY_FILE.write_text(json.dumps(records, indent=2), encoding="utf-8")


def memory_record_summary(record: MemoryRecord) -> Dict[str, object]:
    return {
        "memory_id": record.memory_id,
        "tenant_id": record.tenant_id,
        "project_id": record.project_id,
        "record_type": record.record_type,
        "title": record.title,
        "created_at": record.created_at,
    }