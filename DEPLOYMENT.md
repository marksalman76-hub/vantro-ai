# Deployment Guide

Complete procedure for deploying updates (security patches, features, fixes) to the Vantro AI system.

---

## Development → Production Workflow

### Phase 1: Development & Testing (Local + CI)

#### 1. Create feature branch
```bash
git checkout -b feature/your-feature-name
```

#### 2. Make code changes
- Backend: `backend/app/routes/`, `backend/app/services/`, `backend/app/models/`
- Frontend: `frontend/app/`, `frontend/components/`
- Tests: `backend/tests/`

#### 3. Run local tests before pushing
```bash
# Backend unit tests
cd backend
python -m pytest tests/ -v

# Frontend lint & type check
cd ../frontend
npm run lint
npx tsc --noEmit
```

#### 4. Commit with clear message
```bash
git commit -m "Feature: add two-factor authentication

- Add TOTP-based 2FA to user model
- Implement /api/auth/2fa/setup endpoint
- Add 2FA verification to login flow
- Update frontend with 2FA UI
- Add integration tests for 2FA"
```

#### 5. Push feature branch
```bash
git push origin feature/your-feature-name
```

**CI pipeline auto-runs:**
- ✅ Backend pytest (SQLite, no DB required)
- ✅ Frontend ESLint + TypeScript
- ✅ Docker build validation (both API + worker Dockerfiles)

If any step fails → fix and push again. CI won't pass until all checks green.

---

### Phase 2: Code Review → Merge

#### 1. Create Pull Request
- Title: clear, under 70 chars
- Description: what changed, why, test plan

#### 2. Address review comments
- If reviewer requests changes: commit fixes, push again (don't amend)
- CI re-runs automatically on each push

#### 3. Merge to main
- Requires CI to pass
- Optionally requires approval (configure in branch protection rules)

```bash
# After merge, the branch is deleted automatically (optional in GH settings)
```

**Important:** Do NOT push to `main` manually. Always merge via Pull Request so CI runs first.

---

### Phase 3: Automated Deployment (Deploy Pipeline)

Once merged to `main`, GitHub Actions `deploy.yml` automatically triggers:

#### **Step 1: Build** (3–5 min)
- Builds Docker API image: `backend/Dockerfile`
- Builds Docker worker image: `backend/Dockerfile.worker`
- Tags both with `$GITHUB_SHA` (commit hash) + `:latest`
- Pushes to the configured Vantro ECR API repository with the commit SHA tag.

**Monitor:** GitHub Actions tab, "Build & push images" job

#### **Step 2: Database Migration** (1–2 min)
- Runs as ECS one-off task: `alembic upgrade head`
- Reads `DATABASE_URL` from Secrets Manager (RDS prod)
- Applies all pending migrations from `backend/alembic/versions/`
- **Blocks entire deployment if migration fails** (exit code ≠ 0)

**Monitor:** CloudWatch Logs `/ecs/vantro/api` or GitHub Actions log

#### **Step 3: Deploy API & Worker** (5–10 min each, in parallel)
- Renders task definitions with new image SHA
- Registers new task revisions in ECS
- Updates the configured Vantro API and worker ECS services.
- Waits for rolling deployment to stabilize (all tasks healthy)

**Monitor:** 
- GitHub Actions "Deploy API service" / "Deploy worker service" jobs
- ECS console → configured Vantro production cluster → services
- CloudWatch Logs for startup errors

---

## Deployment Checklist

### Before Pushing to Main

- [ ] All code changes completed
- [ ] Local tests pass (`pytest`, `npm run lint`, `tsc --noEmit`)
- [ ] PR created, reviewed, approved
- [ ] No merge conflicts
- [ ] CI pipeline green (all checks passing)

### If Adding Database Changes

- [ ] New migration created in `backend/alembic/versions/` (run `alembic revision --autogenerate -m "your message"`)
- [ ] Migration tested locally against test DB:
  ```bash
  cd backend
  alembic upgrade head  # apply
  alembic downgrade -1  # test rollback (if needed)
  alembic upgrade head  # reapply
  ```
- [ ] Migration file reviewed for correctness (no data loss, no blocking operations on large tables)

### If Changing Secrets/Env Vars

- [ ] Update AWS Secrets Manager:
  ```bash
  aws secretsmanager put-secret-value --secret-id VARIABLE_NAME --secret-string "value" --region us-east-1
  ```
- [ ] Update task definitions if new env var needed:
  - `task-def.json` (API)
  - `task-def-worker.json` (worker)
  - Commit changes, push to trigger re-deploy

### If Changing Infrastructure

- [ ] Update `infra/setup-scale.sh` if needed
- [ ] Test script locally against dev/staging (if available)
- [ ] Document changes in commit message
- [ ] Push changes to main (no auto-deploy for infra, but code is versioned)

---

## Monitoring During Deployment

### Real-Time Checks

**1. GitHub Actions Dashboard**
```
github.com/your-org/ecommerce-ai-agent-platform/actions
```
- Watch the deploy workflow progress
- Each job shows logs; click to expand
- Typical timeline:
  - build: 3–5 min
  - migrate: 1–2 min
  - deploy-api: 5–10 min
  - deploy-worker: 5–10 min
  - **Total: 15–30 min**

**2. AWS ECS Console**
```
https://console.aws.amazon.com/ecs/v2/clusters/$VANTRO_ECS_CLUSTER
```
- Click the configured Vantro API service.
- Under "Deployments" tab, watch task count transition
- Desired = new tasks, Running = healthy tasks
- Goal: all tasks Running before moving to next service

**3. CloudWatch Logs**
```bash
# API logs
aws logs tail /ecs/vantro/api --follow

# Worker logs
aws logs tail /ecs/vantro/worker --follow
```
- Watch for startup errors, warnings
- Expected: "Starting up" → "Listening on 0.0.0.0:8000" or SQS polling

**4. Health Checks**
```bash
# API health
curl https://api.vantro.ai/health
# Expected: {"status": "healthy", "service": "vantro-api"}

# Frontend availability
curl https://vantro.ai
# Expected: 200 OK (HTML page)
```

---

## Rollback Procedure

If deployment fails or introduces issues:

### Option 1: Automatic (ECS Task Stability Timeout)
- If new ECS tasks fail health checks repeatedly
- ECS automatically rolls back to previous task definition
- No manual action needed (happens in ~3–5 min)

### Option 2: Manual Rollback
```bash
# Get previous task definition revision
REVISION=$(aws ecs describe-services \
  --cluster "$VANTRO_ECS_CLUSTER" \
  --services "$VANTRO_API_SERVICE" \
  --region us-east-1 \
  --query 'services[0].taskDefinition' --output text | grep -oE ':[0-9]+$' | sed 's/:/-/')

# Previous revision (e.g., vantro-api:5 if current is vantro-api:6)
PREV_REVISION=$((${REVISION##*-} - 1))

# Revert service to previous task def
aws ecs update-service \
  --cluster "$VANTRO_ECS_CLUSTER" \
  --service "$VANTRO_API_SERVICE" \
  --task-definition vantro-api:$PREV_REVISION \
  --force-new-deployment \
  --region us-east-1
```

### Option 3: Revert Code & Re-Deploy
If the code change itself is problematic:
```bash
git revert HEAD  # Create a new commit that undoes the last one
git push origin main
# Deploy pipeline re-runs with reverted code
```

---

## Security Patch Deployment

For urgent security fixes:

### 1. Create hotfix branch
```bash
git checkout -b hotfix/security-cve-2024-xxxxx
```

### 2. Apply fix (minimal change)
- Only fix the security issue
- Don't include unrelated refactoring
- Add security test to `backend/tests/test_security_fixes.py`

### 3. Push for immediate review & merge
```bash
git push origin hotfix/security-cve-2024-xxxxx
# Create PR with [SECURITY] tag in title
```

### 4. Fast-track merge
- Expedited review (target: <30 min)
- Merge to main immediately upon approval
- Deploy pipeline auto-runs

### 5. Post-deployment
- Monitor logs for 30 min
- Notify customers if data exposure occurred (legal/compliance)

---

## Feature Flag Deployments (for large changes)

For risky features, use a feature flag to deploy code but keep feature hidden:

### 1. Wrap new code in flag
```python
# backend/app/routes/auth.py
if os.getenv("FEATURE_2FA_ENABLED") == "true":
    @router.post("/api/auth/2fa/setup")
    async def setup_2fa(...):
        ...
```

### 2. Deploy with flag disabled
```bash
# Push to main with FEATURE_2FA_ENABLED=false in Secrets Manager
# Code deploys but feature is inactive
```

### 3. Test in production (without affecting users)
```bash
# Temporarily enable flag for internal testing
aws secretsmanager put-secret-value \
  --secret-id FEATURE_2FA_ENABLED --secret-string "true" --region us-east-1

# Restart ECS tasks to pick up new secret
aws ecs update-service --cluster "$VANTRO_ECS_CLUSTER" \
  --service "$VANTRO_API_SERVICE" --force-new-deployment --region us-east-1

# Test feature
# ...

# Re-disable when ready for public rollout
```

### 4. Gradually enable for users
- Set flag to `true` for 10% of users (via random check)
- Monitor error rates, logs
- Gradually increase percentage
- Full rollout when stable

---

## Performance & Load Testing Before Production

For major changes that could impact performance:

### 1. Load test locally
```bash
# Install locust
pip install locust

# Create locustfile.py with user scenarios
# Run: locust -f locustfile.py --headless -u 1000 -r 50 -t 5m

# Acceptable thresholds:
# - p95 latency < 500ms (API)
# - Error rate < 0.1%
# - CPU < 80%
```

### 2. Stage in dev/staging cluster (if available)
- Deploy to non-prod ECS cluster first
- Run similar load test against staging
- Verify metrics are acceptable

### 3. Canary deployment to production
- Deploy to 1 task (1/20 replicas)
- Monitor for 30 min
- Gradually increase to 100%

---

## Post-Deployment Verification

After deployment completes:

### 1. Smoke tests (5 min)
```bash
# Health check
curl https://api.vantro.ai/health
curl https://api.vantro.ai/

# Frontend loads
curl https://vantro.ai/login --silent | grep -q "vantro" && echo "✅ Frontend OK"

# Key endpoints
curl -H "Authorization: Bearer $TEST_TOKEN" https://api.vantro.ai/api/auth/me
```

### 2. Monitor metrics (30 min)
- CloudWatch Dashboards: check CPU, memory, request latency
- Error rate: should be <0.1%
- SQS queue depth: should be processing normally (not backing up)
- Redis hit rate: should be >70% (if using cache)

### 3. Check logs for warnings
```bash
aws logs filter-log-events \
  --log-group-name /ecs/vantro/api \
  --start-time $(date -d '10 minutes ago' +%s)000 \
  --filter-pattern "ERROR"
```
- If any errors, review and rollback if needed

### 4. Notify stakeholders
- Deployment complete
- All systems nominal
- Link to change log (PR merge commit)

---

## Emergency Contacts & Escalation

| Issue | Action |
|-------|--------|
| API down | Check ECS task status, review CloudWatch logs, rollback if needed |
| DB migration failed | Check migration logs, fix schema issue, re-run `alembic upgrade head` |
| Worker queue backing up | Check SQS queue, verify HeyGen API key is valid, scale worker tasks |
| High error rate | Check logs, identify root cause, rollback if critical |
| Security incident | Follow incident response plan, disable compromised feature flag, notify team |

---

## Deployment Frequency

**Recommended:**
- **Hotfixes (security):** Deploy immediately (no waiting)
- **Bug fixes:** Deploy ASAP (same day if possible)
- **Features:** Deploy on regular cadence (e.g., Tuesdays 2pm UTC) to minimize surprises
- **Infrastructure changes:** Schedule in advance, deploy during low-traffic window

**Current system capacity:** Can handle multiple deployments per day without downtime (rolling updates).

---

## Useful Commands Cheat Sheet

```bash
# View current ECS service status
aws ecs describe-services --cluster "$VANTRO_ECS_CLUSTER" \
  --services "$VANTRO_API_SERVICE" "$VANTRO_WORKER_SERVICE" --region us-east-1

# Stream API logs
aws logs tail /ecs/vantro/api --follow --region us-east-1

# Force new deployment (if needed)
aws ecs update-service --cluster "$VANTRO_ECS_CLUSTER" \
  --service "$VANTRO_API_SERVICE" --force-new-deployment --region us-east-1

# View task definitions
aws ecs list-task-definitions --family-prefix vantro-api --region us-east-1

# Manually run migration ECS task (if needed)
aws ecs run-task --cluster "$VANTRO_ECS_CLUSTER" \
  --task-definition vantro-api \
  --overrides '{"containerOverrides":[{"name":"api","command":["alembic","upgrade","head"]}]}' \
  --launch-type FARGATE --region us-east-1

# Check SQS queue depth
aws sqs get-queue-attributes --queue-url https://sqs.us-east-1.amazonaws.com/685570573617/vantro-video-jobs.fifo \
  --attribute-names ApproximateNumberOfMessages --region us-east-1
```
