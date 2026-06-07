CREATE TABLE IF NOT EXISTS provider_execution_records (
    execution_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    project_id TEXT NOT NULL DEFAULT 'default_project',
    agent_id TEXT,
    provider TEXT NOT NULL,
    capability TEXT,
    action_type TEXT,
    status TEXT NOT NULL,
    request_hash TEXT,
    idempotency_key TEXT,
    request_id TEXT NOT NULL DEFAULT 'unknown_request',
    provider_key TEXT,
    task_type TEXT,
    execution_status TEXT,
    worker_job_id TEXT,
    provider_job_id TEXT,
    extra_json JSONB DEFAULT '{}'::jsonb,
    live_external_call_executed BOOLEAN DEFAULT FALSE,
    customer_safe BOOLEAN DEFAULT TRUE,
    credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at_ms BIGINT DEFAULT ((EXTRACT(EPOCH FROM NOW()) * 1000)::BIGINT),
    updated_at_ms BIGINT DEFAULT ((EXTRACT(EPOCH FROM NOW()) * 1000)::BIGINT)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_provider_execution_idempotency
ON provider_execution_records (tenant_id, provider, idempotency_key)
WHERE idempotency_key IS NOT NULL AND idempotency_key <> '';

CREATE INDEX IF NOT EXISTS idx_provider_execution_records_tenant_id
ON provider_execution_records (tenant_id);

CREATE INDEX IF NOT EXISTS idx_provider_execution_records_provider
ON provider_execution_records (provider);

CREATE TABLE IF NOT EXISTS provider_jobs (
    provider_job_id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    provider_external_job_id TEXT,
    tenant_id TEXT NOT NULL,
    project_id TEXT NOT NULL DEFAULT 'default_project',
    status TEXT NOT NULL,
    polling_status TEXT,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    next_poll_at TIMESTAMPTZ,
    next_retry_at TIMESTAMPTZ,
    last_error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    failed_at TIMESTAMPTZ,
    credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_provider_jobs_execution
ON provider_jobs (execution_id);

CREATE INDEX IF NOT EXISTS idx_provider_jobs_tenant_status
ON provider_jobs (tenant_id, status, created_at);

CREATE TABLE IF NOT EXISTS provider_job_events (
    event_id TEXT PRIMARY KEY,
    provider_job_id TEXT,
    execution_id TEXT,
    event_type TEXT NOT NULL,
    payload_json JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_provider_job_events_execution
ON provider_job_events (execution_id);

CREATE TABLE IF NOT EXISTS provider_dispatch_attempts (
    dispatch_attempt_id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL,
    provider_job_id TEXT,
    provider TEXT NOT NULL,
    status TEXT NOT NULL,
    idempotency_key TEXT,
    latency_ms INTEGER DEFAULT 0,
    error TEXT,
    attempt_number INTEGER,
    allowed_by_policy BOOLEAN,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_provider_dispatch_idempotency
ON provider_dispatch_attempts (provider, idempotency_key)
WHERE idempotency_key IS NOT NULL AND idempotency_key <> '';

CREATE INDEX IF NOT EXISTS idx_provider_dispatch_attempts_execution
ON provider_dispatch_attempts (execution_id);

CREATE TABLE IF NOT EXISTS provider_retry_history (
    retry_id TEXT PRIMARY KEY,
    provider_job_id TEXT,
    execution_id TEXT NOT NULL,
    retry_reason TEXT NOT NULL,
    attempt_number INTEGER NOT NULL,
    scheduled_for TIMESTAMPTZ,
    retry_allowed BOOLEAN,
    next_action TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_provider_retry_history_execution
ON provider_retry_history (execution_id);

CREATE TABLE IF NOT EXISTS provider_polling_state (
    provider_job_id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    polling_status TEXT NOT NULL,
    next_poll_at TIMESTAMPTZ,
    last_poll_at TIMESTAMPTZ,
    provider_status TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS provider_result_records (
    result_id TEXT PRIMARY KEY,
    provider_job_id TEXT,
    execution_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    result_status TEXT NOT NULL,
    result_summary TEXT,
    asset_id TEXT,
    asset_url TEXT,
    metadata_json JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS provider_delivery_packets (
    delivery_packet_id TEXT PRIMARY KEY,
    provider_job_id TEXT,
    execution_id TEXT NOT NULL,
    asset_id TEXT,
    delivery_status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS provider_latency_metrics (
    metric_id TEXT PRIMARY KEY,
    tenant_id TEXT,
    request_id TEXT,
    execution_id TEXT,
    provider TEXT NOT NULL,
    capability TEXT,
    latency_ms INTEGER NOT NULL,
    status TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    credential_values_exposed BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_provider_latency_metrics_tenant_provider
ON provider_latency_metrics (tenant_id, provider);
