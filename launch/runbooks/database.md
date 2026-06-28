# Database Operations Runbook — Vantro.ai Production

**RDS instance:** `vantro-prod-db`
**Engine:** PostgreSQL (Multi-AZ recommended)
**ORM:** SQLAlchemy + Alembic (migrations 001 → 021)
**Owner:** mark.salman76@gmail.com
**Last updated:** 2026-06-28

> SECURITY RULE — NEVER VIOLATE:
> Do NOT `SELECT encrypted_value FROM workspace_integrations` in any context.
> That column holds AES-128-CBC encrypted third-party credentials. If you need to
> inspect a credential, use the `/test` integration endpoint which decrypts in-process
> and returns only a masked preview.

---

## Table of Contents

1. [Connecting to RDS in Production](#1-connecting-to-rds-in-production)
2. [Manual SQL — Safe Patterns](#2-manual-sql--safe-patterns)
3. [Running Alembic Migrations](#3-running-alembic-migrations)
4. [Backup Verification](#4-backup-verification)
5. [Restore from Snapshot](#5-restore-from-snapshot)
6. [Connection Pool Monitoring](#6-connection-pool-monitoring)
7. [Common Operational Queries](#7-common-operational-queries)
8. [pgvector / Skill RAG](#8-pgvector--skill-rag)
9. [Emergency Escalation](#9-emergency-escalation)

---

## 1. Connecting to RDS in Production

RDS has **no public endpoint**. Two access paths:

### 1a. Via ECS Exec (preferred — zero bastion needed)

```bash
# List running tasks to find a task ARN
aws ecs list-tasks --cluster vantro-prod --service-name vantro-backend-service

# Open an interactive shell into the backend container
aws ecs execute-command \
  --cluster vantro-prod \
  --task <task-arn> \
  --container vantro-backend \
  --command "/bin/bash" \
  --interactive

# Inside the container, DATABASE_URL is already set from Secrets Manager
psql $DATABASE_URL
```

Requirements: `aws ecs execute-command` needs `ssmmessages:*` permissions on the task role
and `enableExecuteCommand: true` on the ECS service. If the command is refused, check the
task role in IAM.

### 1b. Via SSM Session Manager (EC2 bastion or NAT instance)

```bash
# Find the bastion instance ID
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=vantro-bastion" \
  --query 'Reservations[*].Instances[*].[InstanceId,State.Name]' \
  --output table

# Start a session (no SSH key needed — SSM handles auth)
aws ssm start-session --target <instance-id>

# Inside the session, fetch the DB URL from Secrets Manager and connect
export DATABASE_URL=$(aws secretsmanager get-secret-value \
  --secret-id vantro/prod/backend \
  --query 'SecretString' --output text | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(d['DATABASE_URL'])")

psql $DATABASE_URL
```

### 1c. Via SSH tunnel (if a bastion EC2 exists with port 22 open)

```bash
# Tunnel: local port 5432 → RDS endpoint port 5432 via bastion
ssh -N -L 5432:<rds-endpoint>:5432 ec2-user@<bastion-public-ip> -i ~/.ssh/vantro-prod.pem &

# Then connect locally (password from Secrets Manager)
psql -h localhost -U vantro_app -d vantro_prod
```

Replace `<rds-endpoint>` with the value from:

```bash
aws rds describe-db-instances \
  --db-instance-identifier vantro-prod-db \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text
```

---

## 2. Manual SQL — Safe Patterns

### Ground rules

- Always wrap DML in a transaction (`BEGIN` / `COMMIT` / `ROLLBACK`).
- Test on the dev/staging DB first. Dev `DATABASE_URL` is in `.env`.
- Never `UPDATE` without a `WHERE` clause.
- Never `DELETE` without a `WHERE` clause. Prefer soft deletes where the schema supports it.
- Never `SELECT encrypted_value FROM workspace_integrations`.
- Always `EXPLAIN ANALYZE` before running a query on a table with > 100k rows.

### Pattern: ADD COLUMN safely (backward-compatible, no table lock)

```sql
-- Safe: IF NOT EXISTS prevents failure if column already exists
-- Nullable column with no default = instant on large tables (no rewrite)
ALTER TABLE agent_jobs ADD COLUMN IF NOT EXISTS reviewed_by TEXT;

-- Adding a column with a default on PG 11+ is also instant (stored default)
ALTER TABLE credits_accounts ADD COLUMN IF NOT EXISTS currency TEXT NOT NULL DEFAULT 'USD';
```

### Pattern: CREATE INDEX without blocking reads/writes

```sql
-- CONCURRENTLY builds the index without holding a lock
-- Takes longer but does not block the application
CREATE INDEX CONCURRENTLY IF NOT EXISTS
  idx_agent_jobs_workspace_status
  ON agent_jobs (workspace_id, status);

-- Check progress while building
SELECT phase, blocks_done, blocks_total
FROM pg_stat_progress_create_index
WHERE relid = 'agent_jobs'::regclass;
```

Never use plain `CREATE INDEX` on a live production table. Always use `CONCURRENTLY`.

### Pattern: Bulk UPDATE with LIMIT and audit trail

```sql
-- Safe bulk update: batches, RETURNING lets you audit what changed
BEGIN;

UPDATE agent_jobs
SET status = 'failed',
    error_message = 'Manually expired by operator on 2026-06-28',
    updated_at = NOW()
WHERE status = 'pending'
  AND created_at < NOW() - INTERVAL '2 hours'
  AND id IN (
    SELECT id FROM agent_jobs
    WHERE status = 'pending'
      AND created_at < NOW() - INTERVAL '2 hours'
    LIMIT 500          -- process in batches; run multiple times if needed
    FOR UPDATE SKIP LOCKED
  )
RETURNING id, workspace_id, agent_id, created_at;

-- Review the RETURNING output before committing
COMMIT;
```

### Pattern: Fix a specific workspace's credit balance

```sql
BEGIN;

-- 1. Inspect current state
SELECT ca.id, ca.balance, ca.total_spent, w.name
FROM credits_accounts ca
JOIN workspaces w ON w.id = ca.workspace_id
WHERE ca.workspace_id = '<workspace_uuid>';

-- 2. Apply correction with a comment (balance is in credits, not dollars)
UPDATE credits_accounts
SET balance = balance + 500,          -- add 500 credits
    updated_at = NOW()
WHERE workspace_id = '<workspace_uuid>';

-- 3. Verify
SELECT balance FROM credits_accounts WHERE workspace_id = '<workspace_uuid>';

COMMIT;
```

---

## 3. Running Alembic Migrations

### Standard upgrade (apply all pending)

```bash
# From inside the backend container or a local dev env with DATABASE_URL set
cd backend
alembic upgrade head
```

### Check current revision

```bash
alembic current
```

### Dry-run — see SQL without executing

```bash
alembic upgrade head --sql
```

### Downgrade one step (emergency rollback)

```bash
alembic downgrade -1
```

### Generate a new migration after model change

```bash
alembic revision --autogenerate -m "add_reviewed_by_to_agent_jobs"
# Always review the generated file in alembic/versions/ before applying
```

### Production migration checklist

- [ ] Migration tested on staging with production-sized data.
- [ ] No `ALTER TABLE ... ADD COLUMN NOT NULL` without a default on large tables.
- [ ] No plain `CREATE INDEX` — use `CONCURRENTLY` in a raw SQL migration if needed.
- [ ] Downgrade path tested.
- [ ] Application deployed with backward-compatible code **before** the migration runs
      (expand-then-contract pattern for column renames/removals).

---

## 4. Backup Verification

### List automated and manual snapshots

```bash
aws rds describe-db-snapshots \
  --db-instance-identifier vantro-prod-db \
  --query 'DBSnapshots[*].[DBSnapshotIdentifier,SnapshotCreateTime,Status,SnapshotType]' \
  --output table
```

### Confirm automated backups are enabled (should return >= 7)

```bash
aws rds describe-db-instances \
  --db-instance-identifier vantro-prod-db \
  --query 'DBInstances[0].BackupRetentionPeriod' \
  --output text
```

If this returns `0`, automated backups are disabled — fix immediately:

```bash
aws rds modify-db-instance \
  --db-instance-identifier vantro-prod-db \
  --backup-retention-period 14 \
  --apply-immediately
```

### Trigger a manual snapshot before any risky operation

```bash
aws rds create-db-snapshot \
  --db-instance-identifier vantro-prod-db \
  --db-snapshot-identifier "vantro-manual-$(date +%Y%m%d-%H%M)"
```

Wait for it to complete:

```bash
aws rds wait db-snapshot-completed \
  --db-snapshot-identifier "vantro-manual-$(date +%Y%m%d)"
echo "Snapshot ready"
```

### Verify backup window and maintenance window

```bash
aws rds describe-db-instances \
  --db-instance-identifier vantro-prod-db \
  --query 'DBInstances[0].{Backup:PreferredBackupWindow,Maintenance:PreferredMaintenanceWindow,MultiAZ:MultiAZ}'
```

---

## 5. Restore from Snapshot

> Full restore creates a NEW RDS instance. The existing instance is untouched until you
> cut over. This is intentional — you always have a fallback.

### Step 1 — Restore snapshot to a new instance

```bash
SNAPSHOT_ID="vantro-manual-20260628-1200"   # replace with actual snapshot ID
NEW_INSTANCE="vantro-prod-db-restored"

aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier "$NEW_INSTANCE" \
  --db-snapshot-identifier "$SNAPSHOT_ID" \
  --db-instance-class db.t3.medium \          # match prod class
  --no-publicly-accessible \
  --vpc-security-group-ids <sg-id>            # same SG as vantro-prod-db
```

### Step 2 — Wait for availability (can take 10–30 min)

```bash
aws rds wait db-instance-available \
  --db-instance-identifier "$NEW_INSTANCE"
echo "Restored instance is available"
```

### Step 3 — Get the new endpoint

```bash
aws rds describe-db-instances \
  --db-instance-identifier "$NEW_INSTANCE" \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text
```

### Step 4 — Validate data

Connect via SSM/tunnel and run sanity queries:

```sql
SELECT count(*) FROM organizations;
SELECT count(*) FROM agent_jobs;
SELECT version_num FROM alembic_version;
```

### Step 5 — Cutover options (choose one)

**Option A — Update Secrets Manager** (zero-infra change, preferred):

```bash
# Get current secret
aws secretsmanager get-secret-value \
  --secret-id vantro/prod/backend \
  --query SecretString --output text

# Update DATABASE_URL to point at restored instance endpoint
aws secretsmanager put-secret-value \
  --secret-id vantro/prod/backend \
  --secret-string '{"DATABASE_URL":"postgresql://vantro_app:<password>@<new-endpoint>:5432/vantro_prod",...}'
```

Then redeploy / force a new ECS task revision so containers pick up the new secret.

**Option B — Update Route 53 CNAME** (if you have a DNS alias for the DB):

```bash
aws route53 change-resource-record-sets \
  --hosted-zone-id <zone-id> \
  --change-batch '{
    "Changes":[{
      "Action":"UPSERT",
      "ResourceRecordSet":{
        "Name":"db.vantro.internal.",
        "Type":"CNAME",
        "TTL":60,
        "ResourceRecords":[{"Value":"<new-endpoint>"}]
      }
    }]
  }'
```

### Step 6 — Run migrations on restored instance if needed

```bash
alembic upgrade head   # run from inside ECS container with new DATABASE_URL
```

### Step 7 — Delete the old/broken instance (only after verifying cutover)

```bash
aws rds delete-db-instance \
  --db-instance-identifier vantro-prod-db \
  --skip-final-snapshot    # only if you have recent snapshots
```

---

## 6. Connection Pool Monitoring

Vantro uses SQLAlchemy's built-in connection pool. Watch for `QueuePool limit of size X
overflow Y reached` errors in CloudWatch Logs — that means the pool is exhausted.

### Check active connections by state (run in psql)

```sql
SELECT
  count(*) AS conn_count,
  state,
  wait_event_type,
  wait_event
FROM pg_stat_activity
WHERE datname = 'vantro_prod'
GROUP BY state, wait_event_type, wait_event
ORDER BY conn_count DESC;
```

### Check max allowed connections

```sql
SHOW max_connections;

-- Also check how close we are
SELECT count(*) AS active, max_conn AS max
FROM pg_stat_activity
CROSS JOIN (SELECT setting::int AS max_conn FROM pg_settings WHERE name='max_connections') s
WHERE datname = 'vantro_prod'
GROUP BY max_conn;
```

### Kill idle connections older than 10 minutes

```sql
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'vantro_prod'
  AND state = 'idle'
  AND query_start < NOW() - INTERVAL '10 minutes'
  AND pid <> pg_backend_pid();   -- never kill your own session
```

### Kill long-running queries (>5 min, excluding backups)

```sql
SELECT pid, now() - query_start AS duration, query, state
FROM pg_stat_activity
WHERE datname = 'vantro_prod'
  AND state != 'idle'
  AND query_start < NOW() - INTERVAL '5 minutes'
  AND query NOT ILIKE '%pg_dump%'
ORDER BY duration DESC;

-- Kill a specific pid after reviewing the query above
SELECT pg_terminate_backend(<pid>);
```

### If pool is consistently exhausted

1. Check CloudWatch for spikes in `DatabaseConnections` metric.
2. Look for the agent_worker loop: if it spawns many concurrent jobs, pool_size may need
   increasing in `app/db/session.py` (`pool_size=`, `max_overflow=`).
3. Alternatively: add PgBouncer in transaction mode in front of RDS.
4. Short-term: scale down concurrent agent workers via `AGENT_WORKER_CONCURRENCY` env var.

---

## 7. Common Operational Queries

All queries assume `psql` is connected to `vantro_prod`. Copy-paste ready.

### 7.1 Check current Alembic migration version

```sql
SELECT version_num FROM alembic_version;
```

### 7.2 Count agent jobs by status

```sql
SELECT status, count(*) AS job_count
FROM agent_jobs
GROUP BY status
ORDER BY job_count DESC;
```

### 7.3 List failed jobs in the last hour

```sql
SELECT
  id,
  workspace_id,
  agent_id,
  error_message,
  created_at
FROM agent_jobs
WHERE status = 'failed'
  AND created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC;
```

### 7.4 Find stuck pending jobs (pending > 30 min — worker may be down)

```sql
SELECT
  id,
  workspace_id,
  agent_id,
  created_at,
  NOW() - created_at AS age
FROM agent_jobs
WHERE status = 'pending'
  AND created_at < NOW() - INTERVAL '30 minutes'
ORDER BY created_at;
```

If rows appear here: check that the `agent_worker` ECS task is running. If the worker
crashed, restarting the ECS service will resume processing.

### 7.5 Check the pending_financial_review queue

These jobs were flagged by `scan_for_financial_actions`. Admin must review.

```sql
SELECT
  id,
  workspace_id,
  agent_id,
  result,
  created_at
FROM agent_jobs
WHERE status = 'pending_financial_review'
ORDER BY created_at DESC;
```

To clear after review (set to completed or failed as appropriate):

```sql
BEGIN;
UPDATE agent_jobs
SET status = 'completed',   -- or 'failed'
    updated_at = NOW()
WHERE id = '<job_uuid>'
  AND status = 'pending_financial_review';
COMMIT;
```

### 7.6 Check workspace credit balance

```sql
SELECT
  w.id AS workspace_id,
  w.name AS workspace_name,
  o.name AS org_name,
  ca.balance,
  ca.total_spent
FROM workspaces w
JOIN organizations o ON o.id = w.organization_id
JOIN credits_accounts ca ON ca.workspace_id = w.id
WHERE w.id = '<workspace_uuid>';
```

### 7.7 Check pending_approval queue (HITL-3 jobs awaiting owner sign-off)

```sql
SELECT
  id,
  workspace_id,
  agent_id,
  created_at,
  NOW() - created_at AS waiting
FROM agent_jobs
WHERE status = 'pending_approval'
ORDER BY created_at;
```

HITL-3 jobs stay here until an admin/owner approves via the admin portal. Do not
manually flip these to `pending` without understanding what the job will do.

### 7.8 List workspaces with zero credits

```sql
SELECT
  w.id,
  w.name,
  o.name AS org,
  ca.balance
FROM workspaces w
JOIN organizations o ON o.id = w.organization_id
JOIN credits_accounts ca ON ca.workspace_id = w.id
WHERE ca.balance <= 0
ORDER BY ca.balance;
```

### 7.9 Count workspace integrations (without touching encrypted values)

```sql
-- Safe: only touches metadata columns, never encrypted_value
SELECT
  wi.integration_type,
  count(*) AS connected_count
FROM workspace_integrations wi
GROUP BY wi.integration_type
ORDER BY connected_count DESC;
```

### 7.10 Find large tables (useful before index operations)

```sql
SELECT
  relname AS table_name,
  pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
  pg_size_pretty(pg_relation_size(relid)) AS table_size,
  pg_size_pretty(pg_total_relation_size(relid) - pg_relation_size(relid)) AS index_size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 15;
```

---

## 8. pgvector / Skill RAG

The `skill_chunks` table stores vector embeddings used by the agent execution pipeline.
When RAG is returning empty results, this table is the first place to check.

### Check chunk count

```sql
SELECT count(*) AS total_chunks FROM skill_chunks;
```

A result of `0` means no skills have been indexed. The application will still work but
agents will not have skill context injected.

### Check chunks per skill

```sql
SELECT skill_name, count(*) AS chunks
FROM skill_chunks
GROUP BY skill_name
ORDER BY chunks DESC;
```

### Trigger a manual reindex

If chunks are 0 or stale (e.g. after adding new skills to `~/.claude/skills/`):

```bash
# From inside a running backend container or via the admin API
curl -X POST https://api.vantro.ai/api/admin/skills/index \
  -H "Authorization: Bearer <admin-token>"
```

Or via ECS exec:

```bash
cd /app
python scripts/index_skills.py
```

Requirements: `OPENAI_API_KEY` must be set in the container environment. If it is missing,
indexing silently skips. Verify:

```bash
echo $OPENAI_API_KEY   # should print a non-empty value (redacted in logs)
```

### Check embedding dimension (should match model output)

```sql
SELECT vector_dims(embedding) AS dims, count(*)
FROM skill_chunks
GROUP BY dims;
```

If dims changes (e.g. after switching embedding models), drop and reindex:

```sql
TRUNCATE TABLE skill_chunks;
-- then reindex via API or script
```

---

## 9. Emergency Escalation

| Situation | First action | Escalation |
|---|---|---|
| DB unreachable | Check ECS task health, SG rules, RDS status in console | Restore from snapshot (Section 5) |
| High connection count | Kill idle connections (Section 6) | Reduce `AGENT_WORKER_CONCURRENCY`, add PgBouncer |
| Stuck pending jobs > 1h | Check agent_worker ECS task, restart service | Manually expire stuck jobs (Section 7.4) |
| Migration failed mid-run | `alembic downgrade -1`, fix migration, retry | Roll back app to previous container image |
| Data corruption suspected | Take manual snapshot immediately (Section 4), investigate | Restore to point-in-time via RDS PITR |
| `encrypted_value` accessed in logs | Treat as security incident — rotate `INTEGRATION_ENCRYPTION_KEY` in Secrets Manager | Audit CloudWatch for any credential exfiltration |

**Solo founder — sole contact:** mark.salman76@gmail.com

AWS RDS Point-in-Time Recovery (PITR) retention: match `BackupRetentionPeriod` (see
Section 4). PITR allows restore to any second within the retention window.

```bash
# PITR restore (replaces snapshot restore when you need a specific timestamp)
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier vantro-prod-db \
  --target-db-instance-identifier vantro-prod-db-pitr \
  --restore-time "2026-06-28T03:00:00Z"
```
