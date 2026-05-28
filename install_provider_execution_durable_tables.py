import os
import psycopg
from pathlib import Path

DATABASE_URL = os.getenv("DATABASE_URL")

env_file = Path(".env.local")
if not DATABASE_URL and env_file.exists():
    for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("DATABASE_URL="):
            DATABASE_URL = line.split("=", 1)[1].strip().strip('"').strip("'")
            break

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not found. Add it to Render/local env before running this migration.")

SQL = """
CREATE TABLE IF NOT EXISTS provider_execution_records (
    execution_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    request_id TEXT NOT NULL,
    provider_key TEXT NOT NULL,
    task_type TEXT NOT NULL,
    execution_status TEXT NOT NULL,
    worker_job_id TEXT,
    provider_job_id TEXT,
    created_at_ms BIGINT NOT NULL,
    updated_at_ms BIGINT NOT NULL,
    live_external_call_executed BOOLEAN DEFAULT FALSE,
    credential_values_exposed BOOLEAN DEFAULT FALSE,
    customer_safe BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS provider_worker_event_ledger (
    ledger_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    request_id TEXT NOT NULL,
    execution_id TEXT NOT NULL,
    worker_job_id TEXT,
    provider_key TEXT NOT NULL,
    event_type TEXT NOT NULL,
    status TEXT NOT NULL,
    details JSONB DEFAULT '{}'::jsonb,
    created_at_ms BIGINT NOT NULL,
    credential_values_exposed BOOLEAN DEFAULT FALSE,
    customer_safe BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS provider_latency_metric_records (
    latency_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    request_id TEXT NOT NULL,
    execution_id TEXT NOT NULL,
    provider_key TEXT NOT NULL,
    latency_ms INTEGER NOT NULL,
    operation TEXT NOT NULL,
    created_at_ms BIGINT NOT NULL,
    credential_values_exposed BOOLEAN DEFAULT FALSE,
    customer_safe BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_provider_execution_records_tenant_request
ON provider_execution_records (tenant_id, request_id);

CREATE INDEX IF NOT EXISTS idx_provider_worker_event_ledger_execution
ON provider_worker_event_ledger (execution_id);

CREATE INDEX IF NOT EXISTS idx_provider_latency_metric_records_execution
ON provider_latency_metric_records (execution_id);
"""

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        cur.execute(SQL)
    conn.commit()

print("PROVIDER_EXECUTION_DURABLE_TABLES_INSTALLED")