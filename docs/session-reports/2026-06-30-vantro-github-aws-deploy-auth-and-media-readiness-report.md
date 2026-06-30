# Vantro GitHub AWS Deploy Auth and Media Readiness Report

**Date:** 2026-06-30  
**Scope:** Work completed after the previous media routing/admin readiness reports.  
**Primary objective:** Restore reliable live media creation by fixing admin Create Media auth, production deploy auth, AWS runtime credentials, and Fargate capacity headroom.

## Executive Summary

This session moved the platform from "provider wiring works in isolated tests, but the live admin UI still fails" to a much cleaner production posture:

- Admin Create Media auth handling was fixed and deployed to the live frontend.
- Vercel production deployment succeeded and `admin.vantro.ai` was confirmed to point at the new deployment.
- GitHub Actions AWS deployment access was repaired by replacing static AWS key secrets with GitHub OIDC.
- AWS ECR/ECS deploy flow was advanced through image builds, ECR pushes, DB migration, API deploy, and worker rollout.
- Production ECS API and worker services reached stable completed rollouts.
- A production Fargate quota increase request was opened for `us-east-1` to prevent future worker deploys from stalling on vCPU placement limits.

The remaining notable issue is naming debt: live AWS infrastructure still contains old `trance-formation` resource names. Those names are internal deployment plumbing, not user-facing product copy, but they should be migrated carefully in a planned infrastructure rename pass.

## What Triggered This Work

The admin dashboard still could not produce media from the browser. The visible console errors were no longer provider execution errors. They showed:

- `401` on `/api/admin-run-agent`
- `401` on admin data routes such as `/api/admin/stats`, `/api/admin/jobs`, `/api/admin/brand-assets`, and `/api/agents`
- `404` noise on old `/dashboard/...` paths

That established the immediate root cause: the browser flow was failing at the admin auth/proxy layer before the media provider execution path could be used.

## Admin Create Media Auth Fix

### Problem

The Create Media page relied heavily on `localStorage.admin_token`. The special `/api/admin-run-agent` route only forwarded the `Authorization` header. Meanwhile, the broader admin proxy already supported the secure `access_token` cookie.

This meant a stale browser token could break media creation even when the backend provider path was healthy.

### Changes Made

Commit:

- `9751b93b Fix admin media auth session handling`

Files changed:

- `frontend/app/api/admin-run-agent/route.ts`
- `frontend/app/admin/create-media/page.tsx`
- `frontend/app/admin-login/page.tsx`

Key behavior changes:

- `/api/admin-run-agent` now reads the secure `access_token` cookie first and falls back to the `Authorization` header.
- Create Media now sends `credentials: include` for API calls.
- Create Media now clears stale local admin/user tokens when a `401` comes back.
- Create Media redirects to `/admin-login` with a clear expired-session error instead of failing silently.
- Admin login now verifies an existing stored admin token before redirecting into `/admin`.

### Validation

Local validation completed:

- Targeted Jest route test passed:
  - `npm test -- frontend/app/api/admin-run-agent/__tests__/route.test.ts`
- Production frontend build passed:
  - `npm run build`

### Deployment

The fix was committed, pushed, and deployed to Vercel production.

Deployment details:

- Vercel deployment ID: `dpl_HPJaER4AMA9aK1BVRaCKRW42n79N`
- Production ready state: `READY`
- Alias confirmed:
  - `admin.vantro.ai`
  - `www.vantro.ai`
  - `vantro.ai`

## Provider Execution and Media Readiness Context

Earlier provider work in the same broader handoff chain had already established:

- Claude Code OAuth token support for production.
- Higgsfield Claude MCP OAuth JSON support.
- Higgsfield MCP credential secret wiring.
- ElevenLabs API key wiring.
- ElevenLabs multilingual TTS success after permissions were corrected.
- Backend live tests reached provider submission paths.

Important commits already in the history:

- `dd2734ce Support Claude OAuth for Higgsfield MCP`
- `fb3084b5 Wire Claude Code OAuth secret into ECS tasks`
- `dae86bab Fail Higgsfield MCP jobs without task ids`
- `17020ca1 Persist Higgsfield Claude MCP OAuth in ECS`

The remaining admin media blocker observed during this session was therefore browser/admin auth, not ElevenLabs or Higgsfield being unwired.

## GitHub AWS Deploy Auth Fix

### Problem

Production GitHub Actions deploys were failing at:

- `Configure AWS credentials`

The workflow still depended on long-lived repository secrets:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

Those were either missing, invalid, or no longer suitable.

### AWS Identity Work Completed

With approval, the AWS account was configured for GitHub OIDC.

Created:

- IAM OIDC provider:
  - `arn:aws:iam::685570573617:oidc-provider/token.actions.githubusercontent.com`
- IAM deploy role:
  - `arn:aws:iam::685570573617:role/GitHubActionsVantroDeployRole`

Trust scope:

- Repository:
  - `marksalman76-hub/vantro-ai`
- Branch subjects:
  - `repo:marksalman76-hub/vantro-ai:ref:refs/heads/main`
  - `repo:marksalman76-hub/vantro-ai:ref:refs/heads/develop`
- Audience:
  - `sts.amazonaws.com`

Attached inline policy:

- ECR auth and image push permissions for the deployment repositories.
- ECS service/task definition deploy permissions.
- ECS run-task permissions for migration.
- IAM pass-role permissions for ECS task roles.

### Workflow Changes

Commit:

- `d4534f38 Use GitHub OIDC for AWS deploys`

Files changed:

- `.github/workflows/deploy.yml`
- `.github/workflows/deploy-staging.yml`

Key workflow changes:

- Added:
  - `permissions: id-token: write`
  - `permissions: contents: read`
- Added:
  - `AWS_ROLE_TO_ASSUME: arn:aws:iam::685570573617:role/GitHubActionsVantroDeployRole`
- Replaced static credential inputs with:
  - `role-to-assume: ${{ env.AWS_ROLE_TO_ASSUME }}`

### Validation

After pushing the workflow change:

- GitHub `Configure AWS credentials` passed.
- GitHub ECR login passed.
- API image push succeeded.
- Worker image push succeeded.

This confirmed GitHub OIDC was working.

## ECR Agent Worker Repository Fix

### Problem

After GitHub AWS auth was fixed, the workflow moved forward and then failed while pushing:

- `trance-formation/agent-worker`

The workflow referenced that ECR repository, but the repository did not exist.

### Change Made

Created ECR repository:

- `685570573617.dkr.ecr.us-east-1.amazonaws.com/trance-formation/agent-worker`

Configuration:

- Region: `us-east-1`
- Encryption: `AES256`
- Image scanning on push: enabled

### Validation

After retriggering deploy:

- API image pushed.
- Worker image pushed.
- Agent-worker image pushed.

## Production Migration Network Config Fix

### Problem

After the image build/push stage was healthy, GitHub deploy failed in the DB migration job at `aws ecs run-task`.

The workflow still referenced subnet/security group values as GitHub secrets:

- `secrets.ECS_SUBNET_IDS`
- `secrets.ECS_SECURITY_GROUP_ID`

Those values were not available or not resolving properly in the workflow.

### Change Made

Commit:

- `236ff532 Fix production deploy migration network config`

File changed:

- `.github/workflows/deploy.yml`

Production network values were made explicit in workflow env because subnet IDs and security group IDs are not secrets:

- `ECS_SUBNET_IDS: subnet-0bf8bad29d2b65b7c,subnet-0e53a96f9db9efb74`
- `ECS_SECURITY_GROUP_ID: sg-0c783bf5d3eb894cc`

The migration command now uses:

- `$ECS_SUBNET_IDS`
- `$ECS_SECURITY_GROUP_ID`

Rollback guard was also tightened so rollback does not fire when earlier stages fail before `deploy-api` has produced a valid previous task definition.

### Validation

After this change:

- Build and image pushes succeeded.
- DB migration succeeded.
- Agent worker deploy step succeeded.
- API deploy succeeded.
- Worker deploy rolled forward.

## ECS Production Rollout Status

Production ECS eventually stabilized after the worker rollout.

Confirmed state:

- API service:
  - Service: `trance-formation-api-service`
  - Desired: `2`
  - Running: `2`
  - Rollout: `COMPLETED`
  - Task definition: `trance-formation-api:16`

- Worker service:
  - Service: `vantro-worker`
  - Desired: `50`
  - Running: `50`
  - Rollout: `COMPLETED`
  - Task definition: `vantro-worker:3`

Live API health was previously verified as:

- `https://api.vantro.ai/health`
- Status: `200`
- Body included:
  - `{"status":"healthy","service":"vantro-api","version":"1.0.0"}`

## Fargate vCPU Quota Issue

### What Happened

During worker deployment, ECS produced placement errors:

- Account had reached the concurrent Fargate vCPU limit.

The account-level applied quota in `us-east-1` was:

- `30` Fargate On-Demand vCPUs

Observed utilization was:

- `26`

The worker service alone uses:

- `50 tasks x 0.5 vCPU = 25 vCPUs`

Rolling deploys need additional temporary headroom. With the quota at 30, ECS had very little room to surge replacement tasks.

### Temporary Deployment Config Adjustment

The worker service deployment configuration was adjusted to reduce surge pressure:

- `maximumPercent: 101`
- `minimumHealthyPercent: 50`

This was needed because AWS rejected `maximumPercent=100` while Availability Zone Rebalancing was enabled.

The rollout completed naturally without reducing desired worker count.

### Quota Request

A quota increase request was opened in the correct production region:

- Region: `us-east-1`
- Service: `AWS Fargate`
- Quota: `Fargate On-Demand vCPU resource count`
- Quota code: `L-3032A538`
- Requested value: `1000`
- Status shown in AWS Console: `Case Opened`

This is the right production quota request. A previous request in `ap-southeast-2` was identified as not relevant to the current production ECS stack.

## Legacy Naming Debt: `trance-formation`

### Current Situation

The live AWS deployment stack still uses legacy internal names:

- ECR:
  - `trance-formation/api`
  - `trance-formation/worker`
  - `trance-formation/agent-worker`
- ECS:
  - `trance-formation-prod`
  - `trance-formation-api-service`
  - `trance-formation-api`

This is why `trance-formation/agent-worker` is still visible in deployment logs and AWS.

### Why It Was Not Removed Immediately

These are live infrastructure identifiers. Removing or renaming them casually would break deployment references, task definitions, and possibly production service updates.

The correct path is a staged AWS naming migration:

1. Create new Vantro-named ECR repositories.
2. Push equivalent images to the new repositories.
3. Register new Vantro-named task definition families where needed.
4. Update ECS services to consume the new task definitions.
5. Confirm production stability.
6. Update GitHub Actions workflow env names and resource targets.
7. Deprecate old `trance-formation` repositories and task families only after rollback windows expire.

This should be tracked as a separate infrastructure cleanup, not bundled into urgent media-production fixes.

## Commits Created During This Work

- `9751b93b Fix admin media auth session handling`
- `d4534f38 Use GitHub OIDC for AWS deploys`
- `f4c6a8fb Trigger deploy after ECR agent worker setup`
- `236ff532 Fix production deploy migration network config`

Relevant earlier commits in this same launch readiness chain:

- `17020ca1 Persist Higgsfield Claude MCP OAuth in ECS`
- `dae86bab Fail Higgsfield MCP jobs without task ids`
- `fb3084b5 Wire Claude Code OAuth secret into ECS tasks`
- `bca339bd Clean launch workspace and media dashboard polish`
- `dd2734ce Support Claude OAuth for Higgsfield MCP`

## Current Status

### Done

- Admin media auth fix deployed to production frontend.
- GitHub AWS static-key failure replaced with OIDC role assumption.
- GitHub deploy can authenticate to AWS.
- GitHub deploy can push API, worker, and agent-worker images to ECR.
- DB migration job can run through ECS.
- API deploy succeeds.
- Worker service reached desired `50/50` running after rollout.
- Production Fargate vCPU quota increase request is open in `us-east-1`.

### Pending

- AWS approval for Fargate On-Demand vCPU quota increase to `1000`.
- Follow-up live media test from the admin Create Media UI after fresh admin login/session refresh.
- Planned internal AWS resource rename away from `trance-formation`.
- Staging deploy workflow validation remains pending because the staging cluster was not found when checked.

## Recommended Next Steps

1. Wait for AWS quota approval.
2. Re-check Fargate applied quota in `us-east-1`.
3. Run a fresh production GitHub deploy after quota approval to confirm worker job no longer times out.
4. Log out and back into `admin.vantro.ai`.
5. Run a live Create Media test with:
   - selected creative agent
   - multilingual option
   - 720p or 1080p first
6. Confirm generated asset appears in Assets and Outputs with preview/download access.
7. Create a separate infrastructure rename plan to remove old `trance-formation` AWS names safely.

## Risk Notes

- Do not delete old `trance-formation` ECR repositories yet. They are still referenced by live workflows/task definitions.
- Do not reduce worker desired count unless explicitly approved during an incident.
- Do not rely on GitHub static AWS secrets going forward; OIDC is now the intended deploy path.
- The Fargate quota request is account and region specific. The production request is the one in `us-east-1`.

