# DevOps Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make GitHub, AWS, Vercel, and Docker operations repeatable through repo-owned checks instead of one-off shell fixes.

**Architecture:** Keep deployment authority in GitHub Actions and Vercel Git integration, while adding a local PowerShell preflight that repairs tool discovery and verifies auth. Add a manual/scheduled GitHub Actions workflow that validates AWS OIDC, Docker builds, and optional Vercel token access without deploying.

**Tech Stack:** PowerShell, GitHub Actions, AWS CLI/OIDC, Docker BuildKit, Vercel CLI.

## Global Constraints

- Do not commit secrets, `.env*`, or `.vercel/` local link files.
- Do not rename existing AWS resources during this automation pass.
- Do not trigger ECS deployments from health checks.
- Production AWS region is `us-east-1`.
- Vercel scope is `marksalman76-5799s-projects`; Vercel project is `vantro-ai`.

---

### Task 1: Local Ops Preflight Script

**Files:**
- Create: `tools/ops-preflight.ps1`
- Modify: `package.json`

**Interfaces:**
- Consumes: local `PATH`, npm global bin, Git, AWS CLI, Docker CLI, Vercel CLI.
- Produces: `npm run ops:preflight` and `npm run ops:fix` commands.

- [x] **Step 1: Add a script that checks and optionally repairs local tool discovery**

Create `tools/ops-preflight.ps1` with checks for Git, GitHub remote, AWS identity, Docker daemon, Vercel auth, and Vercel project link. The `-Fix` mode adds npm global bin to current/user PATH and links the frontend folder to the existing Vercel project.

- [x] **Step 2: Expose npm scripts**

Add `ops:preflight` and `ops:fix` to root `package.json`.

- [x] **Step 3: Verify**

Run: `npm run ops:preflight`

Expected: The script reports missing auth/tooling with actionable commands and exits non-zero only for required blockers.

### Task 2: GitHub Ops Health Workflow

**Files:**
- Create: `.github/workflows/ops-health.yml`

**Interfaces:**
- Consumes: GitHub OIDC role `arn:aws:iam::685570573617:role/GitHubActionsVantroDeployRole`, Dockerfiles, optional `VERCEL_TOKEN`.
- Produces: manual and scheduled health check workflow.

- [x] **Step 1: Add workflow dispatch and weekly schedule**

The workflow runs without deploying and can be triggered manually.

- [x] **Step 2: Validate AWS OIDC**

Run `aws sts get-caller-identity`, describe ECS services, and confirm ECR repositories exist.

- [x] **Step 3: Validate Docker build surfaces**

Build API, worker, and agent-worker images locally in the GitHub runner without pushing.

- [x] **Step 4: Validate Vercel only when token exists**

If `VERCEL_TOKEN` is configured, install Vercel CLI and run `vercel whoami`. If the token is absent, emit a warning and keep the workflow successful.

### Task 3: Permanent Runbook

**Files:**
- Create: `docs/runbooks/devops-automation.md`

**Interfaces:**
- Consumes: scripts and workflows from Tasks 1-2.
- Produces: a concise operating procedure for future sessions.

- [x] **Step 1: Document daily local preflight**

Use `npm run ops:preflight` before deploy work and `npm run ops:fix` when PATH/Vercel link drifts.

- [x] **Step 2: Document GitHub/AWS/Vercel/Docker automation ownership**

Clarify which system handles each concern and which values are intentionally not committed.

- [x] **Step 3: Document the safe deploy rule**

Frontend-only Vercel CLI deploys are allowed for urgent UI fixes; GitHub pushes trigger backend ECS deploys and should wait for quota readiness.
