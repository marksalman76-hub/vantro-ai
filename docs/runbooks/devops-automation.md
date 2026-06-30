# DevOps Automation Runbook

This runbook is the permanent operating path for GitHub, AWS, Vercel, and Docker.

## Daily Local Preflight

Run this before deploy work:

```powershell
npm run ops:preflight
```

If PATH, Vercel linking, or local shell state has drifted:

```powershell
npm run ops:fix
```

For a heavier check that also builds Docker images locally:

```powershell
npm run ops:deep
```

The script checks:

- Git remote and worktree visibility.
- Optional GitHub CLI auth.
- Vercel CLI path, auth, and local project link to `marksalman76-5799s-projects/vantro-ai`.
- AWS CLI identity in `us-east-1`.
- Production ECS service visibility.
- Docker daemon availability.
- Optional local Docker builds in `-Deep` mode.

## GitHub

GitHub Actions is the deployment coordinator for backend and worker infrastructure.

- Production backend deploys run from `.github/workflows/deploy.yml` on `main`.
- Staging backend deploys run from `.github/workflows/deploy-staging.yml` on `develop`.
- Operations health checks run from `.github/workflows/ops-health.yml` manually or on the weekly schedule.

The GitHub AWS deploy role is:

```text
arn:aws:iam::685570573617:role/GitHubActionsVantroDeployRole
```

Do not store AWS access keys in GitHub secrets for this repo. The intended path is GitHub OIDC.

## AWS

Production region:

```text
us-east-1
```

The current production ECS names are still legacy AWS resource names:

```text
Cluster: trance-formation-prod
API service: trance-formation-api-service
Worker service: vantro-worker
Agent worker service: vantro-agent-worker
```

Do not rename or delete these during active launch stabilization. Rename/migrate them only through a separate resource migration plan.

## Docker

Docker images are built by GitHub Actions and pushed to ECR during deploy workflows.

The non-deploying Docker health check is `.github/workflows/ops-health.yml`. It builds:

```text
backend/Dockerfile
backend/Dockerfile.worker
backend/Dockerfile.agent-worker
```

It does not push images and does not update ECS.

## Vercel

The live frontend project is:

```text
Scope: marksalman76-5799s-projects
Project: vantro-ai
Production aliases: admin.vantro.ai, vantro.ai, www.vantro.ai
```

Vercel Git integration should deploy normal frontend changes from GitHub.

For urgent frontend-only fixes where backend/ECS should not be triggered, use a direct Vercel production deploy from `frontend/`:

```powershell
cd frontend
vercel deploy --prod --scope marksalman76-5799s-projects --yes --no-wait
vercel inspect <deployment-url> --scope marksalman76-5799s-projects
```

If `vercel` is not found in a shell, run:

```powershell
npm run ops:fix
```

Then restart VS Code/PowerShell if the current process still has the old PATH.

## GitHub Actions Vercel Token

The ops health workflow can verify Vercel CLI auth when a GitHub secret named `VERCEL_TOKEN` exists.

This token is optional because Vercel Git integration already deploys the frontend. Add it only if we want GitHub Actions to verify Vercel CLI access automatically.

Never commit Vercel tokens, `.env*`, or `.vercel/`.

## Safe Deploy Rule

- Frontend-only emergency UI fix: direct Vercel deploy is acceptable.
- Backend, worker, Docker, task definition, or secret reference change: commit and push through GitHub Actions.
- While Fargate quota is pending, avoid unnecessary backend deploys.
