CREATE TABLE IF NOT EXISTS provider_execution_records (
    execution_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    request_id TEXT NOT NULL,
    provider_key TEXT NOT NULL,
    task_type TEXT NOT NULL,
    execution_status TEXT NOT NULL,
    worker_job_id TEXT,
    provider_job_id TEXT,
    live_external_call_executed BOOLEAN DEFAULT FALSE,
    customer_safe BOOLEAN DEFAULT TRUE,
    credential_values_exposed BOOLEAN DEFAULT FALSE,
    created_at_ms BIGINT NOT NULL,
    updated_at_ms BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS provider_worker_event_ledger (
    ledger_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    request_id TEXT NOT NULL,
    execution_id TEXT NOT NULL,
    worker_job_id TEXT NOT NULL,
    provider_key TEXT NOT NULL,
    event_type TEXT NOT NULL,
    status TEXT NOT NULL,
    details_json TEXT,
    customer_safe BOOLEAN DEFAULT TRUE,
    credential_values_exposed BOOLEAN DEFAULT FALSE,
    created_at_ms BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS provider_dispatch_attempt_records (
    attempt_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    request_id TEXT NOT NULL,
    execution_id TEXT NOT NULL,
    worker_job_id TEXT NOT NULL,
    provider_key TEXT NOT NULL,
    attempt_number INTEGER NOT NULL,
    allowed_by_policy BOOLEAN DEFAULT FALSE,
    result_status TEXT NOT NULL,
    reason TEXT,
    live_external_call_executed BOOLEAN DEFAULT FALSE,
    customer_safe BOOLEAN DEFAULT TRUE,
    credential_values_exposed BOOLEAN DEFAULT FALSE,
    created_at_ms BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS provider_retry_history_records (
    retry_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    request_id TEXT NOT NULL,
    execution_id TEXT NOT NULL,
    worker_job_id TEXT NOT NULL,
    provider_key TEXT NOT NULL,
    attempt_number INTEGER NOT NULL,
    failure_code TEXT NOT NULL,
    retry_allowed BOOLEAN DEFAULT FALSE,
    next_action TEXT NOT NULL,
    customer_safe BOOLEAN DEFAULT TRUE,
    credential_values_exposed BOOLEAN DEFAULT FALSE,
    created_at_ms BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS provider_latency_metric_records (
    latency_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    request_id TEXT NOT NULL,
    execution_id TEXT NOT NULL,
    provider_key TEXT NOT NULL,
    latency_ms INTEGER NOT NULL,
    operation TEXT NOT NULL,
    customer_safe BOOLEAN DEFAULT TRUE,
    credential_values_exposed BOOLEAN DEFAULT FALSE,
    created_at_ms BIGINT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_provider_execution_records_tenant_id ON provider_execution_records(tenant_id);
CREATE INDEX IF NOT EXISTS idx_provider_execution_records_provider_key ON provider_execution_records(provider_key);
CREATE INDEX IF NOT EXISTS idx_provider_worker_event_ledger_tenant_id ON provider_worker_event_ledger(tenant_id);
CREATE INDEX IF NOT EXISTS idx_provider_worker_event_ledger_execution_id ON provider_worker_event_ledger(execution_id);
CREATE INDEX IF NOT EXISTS idx_provider_dispatch_attempt_records_execution_id ON provider_dispatch_attempt_records(execution_id);
CREATE INDEX IF NOT EXISTS idx_provider_retry_history_records_execution_id ON provider_retry_history_records(execution_id);
CREATE INDEX IF NOT EXISTS idx_provider_latency_metric_records_tenant_provider ON provider_latency_metric_records(tenant_id, provider_key);
