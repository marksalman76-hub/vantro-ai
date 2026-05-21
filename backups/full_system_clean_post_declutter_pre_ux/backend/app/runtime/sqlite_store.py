"""
SQLite Store

Production-path persistence foundation for the Ecommerce AI Agent Platform.

This starts the move from JSON-only memory to database-backed runtime storage.
Later this can be upgraded to Postgres without changing the high-level runtime flow.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import json
import sqlite3
import uuid


DATA_DIR = Path("backend/app/data")
DB_FILE = DATA_DIR / "ecommerce_ai_runtime.db"


@dataclass
class SQLiteRecord:
    record_id: str
    tenant_id: str
    project_id: str
    record_type: str
    title: str
    payload: Dict[str, object]
    created_at: str


class SQLiteStore:
    def __init__(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(DB_FILE)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS runtime_records (
                    record_id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    record_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_runtime_records_tenant_project ON runtime_records (tenant_id, project_id)"
            )

            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_runtime_records_type ON runtime_records (record_type)"
            )

    def add_record(
        self,
        tenant_id: str,
        project_id: str,
        record_type: str,
        title: str,
        payload: Dict[str, object],
    ) -> SQLiteRecord:
        record = SQLiteRecord(
            record_id=f"dbrec_{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            project_id=project_id,
            record_type=record_type,
            title=title,
            payload=payload,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO runtime_records (
                    record_id,
                    tenant_id,
                    project_id,
                    record_type,
                    title,
                    payload_json,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.record_id,
                    record.tenant_id,
                    record.project_id,
                    record.record_type,
                    record.title,
                    json.dumps(record.payload),
                    record.created_at,
                ),
            )

        return record

    def list_records(
        self,
        tenant_id: Optional[str] = None,
        project_id: Optional[str] = None,
        record_type: Optional[str] = None,
    ) -> List[Dict[str, object]]:
        query = """
            SELECT record_id, tenant_id, project_id, record_type, title, payload_json, created_at
            FROM runtime_records
            WHERE 1 = 1
        """
        params: List[object] = []

        if tenant_id:
            query += " AND tenant_id = ?"
            params.append(tenant_id)

        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)

        if record_type:
            query += " AND record_type = ?"
            params.append(record_type)

        query += " ORDER BY created_at ASC"

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()

        records: List[Dict[str, object]] = []

        for row in rows:
            records.append(
                {
                    "record_id": row[0],
                    "tenant_id": row[1],
                    "project_id": row[2],
                    "record_type": row[3],
                    "title": row[4],
                    "payload": json.loads(row[5]),
                    "created_at": row[6],
                }
            )

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

        return records[-1]


def sqlite_record_summary(record: SQLiteRecord) -> Dict[str, object]:
    return {
        "record_id": record.record_id,
        "tenant_id": record.tenant_id,
        "project_id": record.project_id,
        "record_type": record.record_type,
        "title": record.title,
        "created_at": record.created_at,
    }