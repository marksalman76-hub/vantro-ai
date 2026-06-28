# Vantro.ai Pre-Launch Runbook — T-7 through T-1

**Platform:** Vantro.ai — Multi-tenant B2B SaaS, 27-agent AI workforce  
**Stack:** FastAPI · Next.js 16 · PostgreSQL (RDS) · ECS/Fargate · SQS · ECR · Stripe  
**Cluster:** `vantro` · Service: `backend`  
**Admin:** mark.salman76@gmail.com  
**Related runbooks:** `deploy.md`, `incident-response.md`, `database.md`, `agent-worker.md`

---

## T-7: Code Freeze

### Goal
Lock the `main` branch. No feature merges without explicit emergency exception approval.

### Set Branch Protection via `gh` CLI

```bash
# Require PR reviews, status checks, and no direct pushes to main
gh api repos/{owner}/vantro \
  --method PATCH \
  --field default_branch=main

gh api repos/{owner}/vantro/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["ci/backend-tests","ci/frontend-build"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  --field restrictions=null
```

Replace `{owner}` with your GitHub username or org slug.

### Verify Protection Is Active

```bash
gh api repos/{owner}/vantro/branches/main/protection \
  --jq '{enforce_admins: .enforce_admins.enabled, required_reviews: .required_pull_request_reviews.required_approving_review_count, strict_checks: .required_status_checks.strict}'
```

Expected output:
```json
{
  "enforce_admins": true,
  "required_reviews": 1,
  "strict_checks": true
}
```

### Emergency Exception Process

- [ ] Emergency exceptions require explicit sign-off from **mark.salman76@gmail.com** (sole owner)
- [ ] Post rationale to `#engineering` Slack channel with tag `[EMERGENCY-MERGE]`
- [ ] Temporarily disable protection:
  ```bash
  gh api repos/{owner}/vantro/branches/main/protection \
    --method DELETE
  # Merge the emergency PR
  # Re-enable protection immediately after (rerun PUT command above)
  ```
- [ ] Log the exception in `launch/audit-log.md` with timestamp and justification
- [ ] All emergency merges still require a smoke test run (see T-3 section)

### Code Freeze Checklist

- [ ] Branch protection rule applied and verified
- [ ] All in-flight PRs reviewed — merged or explicitly deferred
- [ ] `git log --oneline -20` reviewed for any uncommitted experiments
- [ ] Staging deployment triggered with frozen `main`:
  ```bash
  git push origin main  # triggers CI → staging deploy
  ```

---

## T-6: Dependency Security Scan

### Goal
Identify and remediate critical and high-severity vulnerabilities in all dependencies.

### Backend: `pip-audit`

```bash
cd backend

# Install pip-audit if needed
pip install pip-audit

# Audit against PyPI advisory database
pip-audit -r requirements.txt --output-format=json > /tmp/pip-audit-report.json

# Human-readable summary
pip-audit -r requirements.txt
```

If a `requirements.lock` or `poetry.lock` exists, prefer:
```bash
pip-audit --requirement requirements.txt --fix --dry-run
```

### Frontend: `npm audit`

```bash
cd frontend

# Full audit with JSON output
npm audit --json > /tmp/npm-audit-report.json

# Summary view
npm audit

# Auto-fix non-breaking upgrades
npm audit fix

# Review what would change before applying breaking fixes
npm audit fix --dry-run
```

### Severity Triage Decision Table

| Severity | Action | Timeline |
|----------|--------|----------|
| **Critical** | Block launch. Must patch before T-0. | Immediate |
| **High** | Block launch unless no patch exists AND risk is accepted in writing by owner. | Before T-1 go/no-go |
| **Medium** | Evaluate exploit vector. If network-accessible, treat as High. Otherwise, log and schedule patch in T+7. | Document decision |
| **Low** | Note in audit log. Patch in next sprint. | No action required pre-launch |
| **Informational** | Ignore for launch purposes. | No action |

### Evaluating a Finding

Ask for each Critical/High finding:
1. Is the vulnerable code path reachable in production?
2. Does an upstream patch exist? `pip-audit --fix` or `npm audit fix`
3. If no patch: is there a configuration workaround?
4. If no workaround: document the accepted risk with owner sign-off.

### Post-Scan Checklist

- [ ] `pip-audit` exits 0 (no critical/high) or all findings documented
- [ ] `npm audit` exits 0 (no critical/high) or all findings documented
- [ ] Any applied patches committed to `main` and deployed to staging
- [ ] Audit reports archived at `launch/security/pip-audit-T6.json` and `launch/security/npm-audit-T6.json`

---

## T-5: Performance Baseline / Load Test

### Goal
Confirm staging handles 50 concurrent users at P95 < 500ms with error rate < 0.1%.

### Install k6

```bash
# macOS
brew install k6

# Linux
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg \
  --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" \
  | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update && sudo apt-get install k6
```

### k6 Script: `launch/load-tests/vantro-baseline.js`

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const agentJobDuration = new Trend('agent_job_submit_duration');

const BASE_URL = __ENV.BASE_URL || 'https://staging.vantro.ai';

export const options = {
  vus: 50,
  duration: '60s',
  thresholds: {
    http_req_duration: ['p(95)<500'],   // P95 < 500ms
    errors: ['rate<0.001'],             // error rate < 0.1%
    http_req_failed: ['rate<0.001'],
  },
};

// Shared state — tokens populated in setup()
let authToken = '';
let workspaceId = '';

export function setup() {
  // Create a test user for the load run
  const signupRes = http.post(`${BASE_URL}/api/auth/register`, JSON.stringify({
    email: `loadtest+${Date.now()}@vantro-staging.internal`,
    password: 'LoadTest_S3cur3!',
    full_name: 'Load Test User',
    organization_name: 'LoadTestOrg',
  }), { headers: { 'Content-Type': 'application/json' } });

  check(signupRes, { 'signup 201': (r) => r.status === 201 });

  const loginRes = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
    email: `loadtest+${Date.now()}@vantro-staging.internal`,
    password: 'LoadTest_S3cur3!',
  }), { headers: { 'Content-Type': 'application/json' } });

  // Fall back to a pre-seeded staging account if signup is rate-limited
  const token = loginRes.json('access_token') || __ENV.STAGING_TOKEN;
  const wsId = loginRes.json('workspace_id') || __ENV.STAGING_WORKSPACE_ID;

  return { token, wsId };
}

export default function (data) {
  const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${data.token}`,
  };

  // Scenario 1: Health check (always fast, baseline sanity)
  const healthRes = http.get(`${BASE_URL}/health`);
  check(healthRes, { 'health 200': (r) => r.status === 200 });
  errorRate.add(healthRes.status !== 200);

  sleep(0.5);

  // Scenario 2: Agent catalogue (27 agents must be returned)
  const catalogueRes = http.get(`${BASE_URL}/api/agents`, { headers });
  const catalogueOk = check(catalogueRes, {
    'catalogue 200': (r) => r.status === 200,
    'catalogue has 27 agents': (r) => {
      try { return JSON.parse(r.body).length === 27; } catch { return false; }
    },
  });
  errorRate.add(!catalogueOk);

  sleep(0.5);

  // Scenario 3: Submit agent job (content_research_agent is HITL-1, fast)
  const jobStart = Date.now();
  const jobRes = http.post(
    `${BASE_URL}/api/agents/content_research_agent/run`,
    JSON.stringify({
      task: 'Summarise the key trends in B2B SaaS for 2026 in 3 bullet points.',
      workspace_id: data.wsId,
    }),
    { headers }
  );
  agentJobDuration.add(Date.now() - jobStart);

  const jobOk = check(jobRes, {
    'job submit 202': (r) => r.status === 202 || r.status === 201,
  });
  errorRate.add(!jobOk);

  const jobId = jobRes.json('job_id');

  sleep(1);

  // Scenario 4: Poll job status
  if (jobId) {
    const pollRes = http.get(`${BASE_URL}/api/agents/jobs/${jobId}`, { headers });
    check(pollRes, {
      'poll 200': (r) => r.status === 200,
      'poll has status': (r) => {
        try {
          const b = JSON.parse(r.body);
          return ['pending', 'running', 'completed', 'failed'].includes(b.status);
        } catch { return false; }
      },
    });
    errorRate.add(pollRes.status !== 200);
  }

  sleep(1);
}

export function teardown(data) {
  // Nothing to clean — staging DB is ephemeral
  console.log('Load test complete. Check k6 summary above for threshold results.');
}
```

### Run the Load Test

```bash
# Against staging
k6 run \
  --vus 50 \
  --duration 60s \
  -e BASE_URL=https://staging.vantro.ai \
  -e STAGING_TOKEN=<pre-seeded-token> \
  -e STAGING_WORKSPACE_ID=<staging-workspace-id> \
  launch/load-tests/vantro-baseline.js

# Save results for comparison
k6 run ... --out json=launch/load-tests/results-T5.json
```

### Pass/Fail Criteria

| Metric | Threshold | Action if Failed |
|--------|-----------|-----------------|
| P95 latency | < 500ms | Investigate slow endpoints, scale ECS task count |
| Error rate | < 0.1% | Check CloudWatch logs, fix before T-0 |
| Agent job submit P95 | < 2000ms | Acceptable for async job submission |
| 27 agents returned | Exactly 27 | Run `python scripts/index_skills.py` and verify registry |

### Post-Test Checklist

- [ ] k6 exits 0 (all thresholds passed)
- [ ] Results archived at `launch/load-tests/results-T5.json`
- [ ] CloudWatch dashboards reviewed during test window for CPU/memory spikes
- [ ] SQS queue depth returned to 0 after test:
  ```bash
  aws sqs get-queue-attributes \
    --queue-url https://sqs.<region>.amazonaws.com/<account>/vantro-jobs \
    --attribute-names ApproximateNumberOfMessages \
    --query 'Attributes.ApproximateNumberOfMessages'
  ```

---

## T-4: Alembic Migration Dry-Run on Staging

### Goal
Verify the production migration chain runs cleanly on a staging database before T-0.

### Step 1: Inspect Migration SQL (dry-run)

Run an ECS one-off task that dumps the SQL without applying it:

```bash
aws ecs run-task \
  --cluster vantro \
  --task-definition vantro-migration \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-XXXXXXXX,subnet-YYYYYYYY],securityGroups=[sg-ZZZZZZZZ],assignPublicIp=DISABLED}" \
  --overrides '{
    "containerOverrides": [{
      "name": "migration",
      "command": [
        "sh", "-c",
        "alembic upgrade head --sql > /tmp/migration.sql && cat /tmp/migration.sql"
      ]
    }]
  }' \
  --region <your-region>
```

Retrieve output via CloudWatch Logs:
```bash
# Get the task ARN from the run-task response, then:
aws logs get-log-events \
  --log-group-name /ecs/vantro-migration \
  --log-stream-name ecs/migration/<task-id> \
  --region <your-region> \
  --query 'events[*].message' \
  --output text
```

Review the SQL for:
- [ ] No `DROP TABLE` or `DROP COLUMN` without corresponding data-safe migration
- [ ] No full-table rewrites on tables with > 100k rows (lock risk)
- [ ] `ALTER TABLE ... ADD COLUMN` with `DEFAULT NULL` or `DEFAULT <value>` (safe)
- [ ] Index creations use `CREATE INDEX CONCURRENTLY` where possible

### Step 2: Apply Migration to Staging

```bash
aws ecs run-task \
  --cluster vantro \
  --task-definition vantro-migration \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-XXXXXXXX,subnet-YYYYYYYY],securityGroups=[sg-ZZZZZZZZ],assignPublicIp=DISABLED}" \
  --overrides '{
    "containerOverrides": [{
      "name": "migration",
      "command": ["alembic", "upgrade", "head"]
    }]
  }' \
  --region <your-region>
```

Wait for the task to reach `STOPPED` state:
```bash
aws ecs wait tasks-stopped \
  --cluster vantro \
  --tasks <task-arn> \
  --region <your-region>
```

### Step 3: Verify Migration Applied

```bash
# Direct psql to staging DB
psql $STAGING_DATABASE_URL -c \
  "SELECT version_num, is_head FROM alembic_version \
   JOIN (SELECT version_num, (version_num = (SELECT version_num FROM alembic_version ORDER BY version_num DESC LIMIT 1)) AS is_head FROM alembic_version) sub USING (version_num);"

# Or simpler — just get current version
psql $STAGING_DATABASE_URL -c "SELECT version_num FROM alembic_version;"
```

Expected: version_num matches the latest revision in `alembic/versions/` (currently `021`).

### Step 4: Rollback Test

Verify the down migration works (on staging only):
```bash
# Roll back one revision
aws ecs run-task \
  --cluster vantro \
  --task-definition vantro-migration \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-XXXXXXXX,subnet-YYYYYYYY],securityGroups=[sg-ZZZZZZZZ],assignPublicIp=DISABLED}" \
  --overrides '{
    "containerOverrides": [{
      "name": "migration",
      "command": ["alembic", "downgrade", "-1"]
    }]
  }' \
  --region <your-region>

# Verify rollback
psql $STAGING_DATABASE_URL -c "SELECT version_num FROM alembic_version;"

# Re-apply to leave staging at head
aws ecs run-task ... # (repeat upgrade command above)
```

### Post-Migration Checklist

- [ ] SQL dry-run reviewed — no destructive statements without justification
- [ ] Migration applied to staging without error
- [ ] `alembic_version` shows expected version (021)
- [ ] Rollback test succeeded
- [ ] Staging app restarted and health check passes post-migration:
  ```bash
  curl -sf https://staging.vantro.ai/health | jq .
  ```

---

## T-3: Staging Smoke Test

### Goal
10-point checklist verifying every critical path works on staging before production deploy.

**Staging base URL:** `https://staging.vantro.ai`

Set up:
```bash
STAGING="https://staging.vantro.ai"
# After running point 2 (signup), capture the token:
TOKEN=""
WORKSPACE_ID=""
```

### Smoke Test Checklist

- [ ] **1. Health check**
  ```bash
  curl -sf $STAGING/health | jq .
  # Expected: {"status": "ok", "db": "connected", "worker": "running"}
  ```

- [ ] **2. Auth: signup**
  ```bash
  curl -sf -X POST $STAGING/api/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email":"smoketest@vantro-staging.internal","password":"Smoke_T3st!","full_name":"Smoke Tester","organization_name":"SmokeOrg"}' \
    | jq '{status: .status, user_id: .user_id}'
  # Expected: 201, user_id present
  ```

- [ ] **3. Auth: login**
  ```bash
  TOKEN=$(curl -sf -X POST $STAGING/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"smoketest@vantro-staging.internal","password":"Smoke_T3st!"}' \
    | jq -r '.access_token')
  echo "Token: ${TOKEN:0:20}..."
  # Expected: non-empty JWT
  ```

- [ ] **4. Workspace creation**
  ```bash
  WORKSPACE_ID=$(curl -sf -X POST $STAGING/api/workspaces \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"name":"Smoke Workspace","tier":"starter"}' \
    | jq -r '.workspace_id')
  echo "Workspace: $WORKSPACE_ID"
  # Expected: UUID, no error
  ```

- [ ] **5. Credits balance**
  ```bash
  curl -sf $STAGING/api/workspaces/$WORKSPACE_ID/credits \
    -H "Authorization: Bearer $TOKEN" \
    | jq '{balance: .balance, tier: .tier}'
  # Expected: balance >= 0, tier = "starter"
  ```

- [ ] **6. Agent catalogue — assert 27 agents**
  ```bash
  COUNT=$(curl -sf $STAGING/api/agents \
    -H "Authorization: Bearer $TOKEN" \
    | jq 'length')
  echo "Agent count: $COUNT"
  [ "$COUNT" = "27" ] && echo "PASS" || echo "FAIL — expected 27, got $COUNT"
  # Expected: 27
  ```

- [ ] **7. Submit agent job**
  ```bash
  JOB_ID=$(curl -sf -X POST $STAGING/api/agents/content_research_agent/run \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"task\":\"List 3 B2B SaaS trends for 2026.\",\"workspace_id\":\"$WORKSPACE_ID\"}" \
    | jq -r '.job_id')
  echo "Job ID: $JOB_ID"
  # Expected: UUID, status=pending
  ```

- [ ] **8. Poll job status**
  ```bash
  sleep 5
  curl -sf $STAGING/api/agents/jobs/$JOB_ID \
    -H "Authorization: Bearer $TOKEN" \
    | jq '{job_id: .job_id, status: .status}'
  # Expected: status one of [pending, running, completed]
  ```

- [ ] **9. Financial review queue empty**
  ```bash
  curl -sf $STAGING/api/admin/financial-review \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    | jq 'length'
  # Expected: 0 (no jobs stuck in pending_financial_review)
  # Alternatively check SQS:
  aws sqs get-queue-attributes \
    --queue-url https://sqs.<region>.amazonaws.com/<account>/vantro-financial-review \
    --attribute-names ApproximateNumberOfMessages \
    --query 'Attributes.ApproximateNumberOfMessages'
  ```

- [ ] **10. Stripe webhook endpoint responds**
  ```bash
  curl -sf -X POST $STAGING/api/billing/webhook \
    -H "Content-Type: application/json" \
    -H "Stripe-Signature: t=0,v1=test" \
    -d '{"type":"ping"}' \
    -o /dev/null -w "%{http_code}"
  # Expected: 400 (invalid signature — proves endpoint is alive and validating)
  # A 404 or 502 means the webhook route is broken
  ```

### Smoke Test Pass Criteria

All 10 points must pass. Any failure blocks launch. Remediate and re-run the full 10-point suite.

---

## T-2: AWS Infrastructure Pre-Check

### Goal
Confirm all production AWS resources are healthy before launch day.

Set your region:
```bash
AWS_REGION=<your-region>
AWS_ACCOUNT=<your-account-id>
```

### ECS — Desired Count and Health

```bash
# Check service desired vs running count
aws ecs describe-services \
  --cluster vantro \
  --services backend \
  --region $AWS_REGION \
  --query 'services[0].{desired:desiredCount,running:runningCount,pending:pendingCount,status:status}'
# Expected: running == desired, pending == 0, status = ACTIVE

# List running tasks
aws ecs list-tasks \
  --cluster vantro \
  --service-name backend \
  --desired-status RUNNING \
  --region $AWS_REGION \
  --query 'taskArns' \
  --output table
```

### RDS — Multi-AZ Verification

```bash
aws rds describe-db-instances \
  --region $AWS_REGION \
  --query 'DBInstances[?DBInstanceIdentifier==`vantro-prod`].{MultiAZ:MultiAZ,Status:DBInstanceStatus,Class:DBInstanceClass,StorageType:StorageType,BackupRetention:BackupRetentionPeriod}' \
  --output table
# Expected: MultiAZ=True, Status=available, BackupRetention >= 7
```

### SQS — Queue Depth Must Be Zero

```bash
# Main job queue
aws sqs get-queue-attributes \
  --queue-url https://sqs.$AWS_REGION.amazonaws.com/$AWS_ACCOUNT/vantro-jobs \
  --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible \
  --region $AWS_REGION \
  --query 'Attributes'
# Expected: ApproximateNumberOfMessages = "0"

# DLQ — must also be empty
aws sqs get-queue-attributes \
  --queue-url https://sqs.$AWS_REGION.amazonaws.com/$AWS_ACCOUNT/vantro-jobs-dlq \
  --attribute-names ApproximateNumberOfMessages \
  --region $AWS_REGION \
  --query 'Attributes.ApproximateNumberOfMessages'
# Expected: "0" — any non-zero value means failed jobs need investigation
```

### CloudWatch Alarms — All Must Be OK

```bash
# List all Vantro/* alarms and their states
aws cloudwatch describe-alarms \
  --alarm-name-prefix "Vantro" \
  --region $AWS_REGION \
  --query 'MetricAlarms[*].{Name:AlarmName,State:StateValue,Reason:StateReason}' \
  --output table
# Expected: StateValue = OK for all alarms
# Any ALARM or INSUFFICIENT_DATA must be investigated before T-0

# Count alarms not in OK state
aws cloudwatch describe-alarms \
  --alarm-name-prefix "Vantro" \
  --state-value ALARM \
  --region $AWS_REGION \
  --query 'length(MetricAlarms)'
# Expected: 0
```

### ECR — Production Image Exists and Is Recent

```bash
# List images in ECR, sorted by push date
aws ecr describe-images \
  --repository-name vantro/backend \
  --region $AWS_REGION \
  --query 'sort_by(imageDetails, &imagePushedAt)[-5:].{tag:imageTags[0],pushed:imagePushedAt,digest:imageDigest}' \
  --output table
# Expected: most recent image pushed within last 24h (from T-3 deploy), tagged with git SHA

# Confirm the ECS service is using the expected image
aws ecs describe-task-definition \
  --task-definition vantro-backend \
  --region $AWS_REGION \
  --query 'taskDefinition.containerDefinitions[0].image'
# Verify this matches the ECR URI of the image you intend to ship
```

### Secrets Manager — All Required Secrets Present

```bash
for secret in vantro/prod/SECRET_KEY vantro/prod/DATABASE_URL vantro/prod/INTEGRATION_ENCRYPTION_KEY vantro/prod/STRIPE_SECRET_KEY vantro/prod/OPENAI_API_KEY; do
  aws secretsmanager describe-secret \
    --secret-id $secret \
    --region $AWS_REGION \
    --query '{name:Name,rotation:RotationEnabled,lastChanged:LastChangedDate}' \
    --output json 2>/dev/null || echo "MISSING: $secret"
done
# Expected: all 5 secrets present, LastChangedDate within last 90 days
```

### Pre-Check Summary Checklist

- [ ] ECS: running count equals desired count, zero pending tasks
- [ ] RDS: Multi-AZ enabled, status available, backup retention >= 7 days
- [ ] SQS job queue: ApproximateNumberOfMessages = 0
- [ ] SQS DLQ: ApproximateNumberOfMessages = 0
- [ ] CloudWatch: zero alarms in ALARM or INSUFFICIENT_DATA state
- [ ] ECR: production image present, pushed within 24h of expected deploy window
- [ ] Secrets Manager: all 5 required secrets present

---

## T-1: On-Call Schedule

### Goal
Confirm human coverage for T-1 through T+7.

### On-Call Coverage Table

| Period | Role | Name | Email | Phone / Slack |
|--------|------|------|-------|---------------|
| T-1 through T+2 | **Primary** | Mark Salman | mark.salman76@gmail.com | `@mark` in Slack |
| T-1 through T+2 | **Secondary** | _(fill in)_ | — | — |
| T+3 through T+7 | **Primary** | Mark Salman | mark.salman76@gmail.com | `@mark` in Slack |
| T+3 through T+7 | **Secondary** | _(fill in)_ | — | — |

**Escalation chain:**
1. Secondary on-call (15-minute response SLA)
2. Primary on-call (immediate)
3. AWS Support (severity 1 case if infrastructure down): [console.aws.amazon.com/support](https://console.aws.amazon.com/support)
4. Stripe support (billing incidents): [support.stripe.com](https://support.stripe.com)

### Confirming the Schedule

- [ ] All on-call engineers have acknowledged their shifts (Slack DM confirmation)
- [ ] PagerDuty / OpsGenie schedule updated (or Slack `#oncall` channel pinned)
- [ ] On-call engineers have verified access to:
  - AWS console with sufficient IAM permissions
  - Production `psql` access via bastion or SSM Session Manager
  - Ability to deploy via `aws ecs update-service` (see `deploy.md`)
  - Sentry org access for error triage
- [ ] Emergency runbook link shared: `launch/runbooks/incident-response.md`
- [ ] Verified Sentry alerts are routing to on-call email/phone

---

## T-1: Go / No-Go Meeting

### Meeting Format

**When:** Day before launch (T-1), ≥ 2 hours before any announcement send  
**Who:** mark.salman76@gmail.com (all gates owned by sole operator)  
**Format:** Review each gate in order. Explicit **GO** or **NO-GO** recorded against each.

### Six-Gate Criteria Table

| # | Gate | Owner | Pass Criteria | Current Status |
|---|------|-------|--------------|----------------|
| 1 | **Security** | Mark Salman | `pip-audit` and `npm audit` return 0 critical/high findings. All medium findings documented with accepted risk. | ☐ Pending |
| 2 | **Performance** | Mark Salman | k6 load test: P95 < 500ms, error rate < 0.1%, all 27 agents returned in catalogue check. Results file exists at `launch/load-tests/results-T5.json`. | ☐ Pending |
| 3 | **Infrastructure** | Mark Salman | All 7 AWS pre-checks green (T-2 checklist fully ticked). Zero CloudWatch alarms in ALARM state. | ☐ Pending |
| 4 | **Migrations** | Mark Salman | Staging `alembic_version` = `021` (or current target). SQL dry-run reviewed. Rollback test passed. Production migration not yet applied — queued for T-0 deploy. | ☐ Pending |
| 5 | **Communications** | Mark Salman | Launch announcement draft finalized and staged. Social posts scheduled but not yet published. Support documentation published to help site. ToS and Privacy Policy URLs active and accessible. | ☐ Pending |
| 6 | **Legal** | Mark Salman | Terms of Service published at `https://vantro.ai/terms`. Privacy Policy published at `https://vantro.ai/privacy`. Cookie consent banner active on marketing site. | ☐ Pending |

### Go/No-Go Decision

```
Date/Time of meeting: ___________________

Gate 1 — Security:       [ GO ] [ NO-GO ]  Notes: ___________
Gate 2 — Performance:    [ GO ] [ NO-GO ]  Notes: ___________
Gate 3 — Infrastructure: [ GO ] [ NO-GO ]  Notes: ___________
Gate 4 — Migrations:     [ GO ] [ NO-GO ]  Notes: ___________
Gate 5 — Communications: [ GO ] [ NO-GO ]  Notes: ___________
Gate 6 — Legal:          [ GO ] [ NO-GO ]  Notes: ___________

FINAL DECISION: [ LAUNCH ] [ DELAY ]

Signed: _________________________ (mark.salman76@gmail.com)
```

A single NO-GO gate delays the launch. Document the blocker, assign a resolution ETA, and reschedule the meeting.

---

## Communication Hold

### Draft Location

The launch announcement draft lives at:
```
launch/comms/launch-announcement-draft.md
```

Supporting assets (social copy, email HTML) live at:
```
launch/comms/
├── launch-announcement-draft.md   # Primary announcement
├── twitter-thread.md              # Twitter/X thread
├── linkedin-post.md               # LinkedIn announcement
├── email-blast.html               # Customer email (Resend / Mailchimp)
└── product-hunt-tagline.md        # If launching on PH
```

### Who Holds the Send Key

**Send authority:** mark.salman76@gmail.com exclusively.  
No announcement goes out until the Go/No-Go meeting returns a **LAUNCH** decision.

### Trigger for Release

The communication hold lifts when **all** of the following are true:

1. All 6 Go/No-Go gates are marked **GO**
2. Production deploy (`deploy.md` T-0 procedure) completed successfully
3. Post-deploy smoke test (10-point checklist from T-3 section, run against `https://vantro.ai`) passes
4. First real Stripe payment endpoint verified via `curl` against production
5. Mark sends explicit "comms released" message in `#engineering` Slack channel

### Release Sequence

```
T-0: Production deploy complete
  └─> Run 10-point smoke test against production
      └─> All 10 pass?
          YES → Mark posts "comms released" to #engineering
                 └─> Publish announcement (Product Hunt, Twitter, LinkedIn, email)
          NO  → Hold comms, invoke incident-response.md, reassess ETA
```

### Rollback Trigger

If production is rolled back after comms go out:
1. Post holding message: "We're experiencing some issues — investigating now"
2. Invoke `incident-response.md` immediately
3. Do NOT post further updates until root cause is understood

---

## Reference

| Document | Path |
|----------|------|
| Deploy runbook | `launch/runbooks/deploy.md` |
| Incident response | `launch/runbooks/incident-response.md` |
| Database operations | `launch/runbooks/database.md` |
| Agent worker ops | `launch/runbooks/agent-worker.md` |
| Load test script | `launch/load-tests/vantro-baseline.js` |
| Security scan reports | `launch/security/` |
| Comms drafts | `launch/comms/` |
| Audit log | `launch/audit-log.md` |

---

*Last updated: T-7 pre-launch prep. Owner: mark.salman76@gmail.com*
