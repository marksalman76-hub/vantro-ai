# Vantro Session Report - Admin, Deployment, Creative Provider Routing, and Media Execution

Date: 2026-06-30  
Repository: `marksalman76-hub/vantro-ai`  
Primary domains: `vantro.ai`, `admin.vantro.ai`, `api.vantro.ai`  
Primary live admin route: `https://admin.vantro.ai/admin`  

## Executive Summary

This session focused on stabilizing Vantro's live production experience, locking the public site to the canonical `vantro.ai` deployment, restoring admin access through the `admin.vantro.ai` subdomain, wiring creative agents to the canonical provider-routing layer, and debugging the Create Media execution path.

The most important outcome is that the live public experience is canonical at `vantro.ai`, the admin app is behind `admin.vantro.ai`, and Create Media now routes through a Vercel-side admin run proxy that can fall back to the standard agent execution endpoint when the backend admin route returns a server error.

The session also locked in creative provider routing rules for Higgsfield video models and Nano Banana image models, added admin unlimited-credit display behavior, installed and used Vercel CLI, pushed multiple production commits to GitHub, and verified multiple Vercel production deployments.

## Canonical Public Site

Actions completed:

- Confirmed the intended public site is `https://vantro.ai`.
- Kept the canonical Vantro production deployment intact.
- Confirmed `vantro.ai` is the public production URL.
- Confirmed the admin app should not live under `vantro.ai/admin-*`; admin routes were intended to live under `admin.vantro.ai`.

Result:

- Public website direction was clarified and locked to one canonical live site.
- Prior public-site variants are no longer referenced as part of the intended live production surface.

## Admin Domain and Route Separation

The admin experience was moved away from the public domain route confusion.

Important decisions:

- Public website: `https://vantro.ai`
- Admin website: `https://admin.vantro.ai`
- Admin login: `https://admin.vantro.ai/admin-login`
- Admin dashboard: `https://admin.vantro.ai/admin`
- Create Media: `https://admin.vantro.ai/admin/create-media`

Observed issue:

- `https://vantro.ai/admin-login` returned a 404 after admin routes were restricted away from the public domain.
- This was expected after the admin route separation.

Result:

- The correct admin entry point is `admin.vantro.ai/admin-login`, not `vantro.ai/admin-login`.
- The public Vantro domain is reserved for the public/client website.

## Admin Login and Dashboard Work

The admin login surfaced several authentication and routing issues during the session.

Observed states:

- `localhost:3001/admin-login` showed the admin login UI but the local API call returned `500`.
- `admin.vantro.ai/admin-login` loaded the production admin login.
- At one point, the login page showed "Network error - is the server running?", indicating the frontend could not reach the backend correctly or the backend route was returning a failure.

After admin login was working, the admin dashboard showed `0 credits`, which was misleading for the owner/admin account.

Fix completed:

- Admin dashboard was changed to show unlimited owner credits.
- Commit: `bcbc5a4a Show unlimited credits for admin dashboard`

Result:

- The owner/admin dashboard now represents owner access as unlimited rather than showing `0 credits`.

## Brand Asset Upload and Create Media UX

The Create Media flow originally did not clearly show upload functionality.

Actions completed:

- Added or restored visible upload controls in the Create Media flow.
- The Upload References area now shows an `Upload file` button and links to Manage Brand Assets.
- Brand asset selection and uploaded reference file metadata are included in the Create Media request context.

Relevant behavior:

- Create Media builds a task prompt from:
  - media type
  - brief
  - platform
  - aspect ratio
  - tone
  - creator age/gender/ethnicity
  - language
  - video quality
  - brand profile preference
  - selected brand assets
  - uploaded reference file metadata

Result:

- The Create Media screen now gives the admin a practical way to attach reference assets and context before submitting a media generation task.

## Creative Provider Routing

The user approved the canonical creative provider routing design in:

`docs/superpowers/specs/2026-06-29-creative-provider-routing-design.md`

Routing rules approved and implemented:

- Video `720p` routes to Higgsfield model `Kling 3.0 Turbo`.
- Video `1080p` routes to Higgsfield model `Kling 3.0`.
- Video `4K` routes to Higgsfield model `Cinema Studio 4K`.
- Standard or production image requests route to `Nano Banana 2`.
- Premium or pro image requests route to `Nano Banana Pro`.

Creative-capable agent aliases and IDs covered include:

- `ugc_media_agent`
- `ugc_creative_agent`
- `product_image_agent`
- `ad_creative_agent`
- `creative_rotation_agent`
- `social_media_content_agent`
- `ads_optimisation_agent`
- `product_video_agent` aliasing into the UGC media route

Files involved:

- `backend/app/runtime/creative_provider_routing.py`
- `backend/app/runtime/audio_visual_provider_stack.py`
- `backend/app/routes/admin.py`
- `backend/app/agents/agent_worker.py`
- `backend/app/integrations/execution_adapters.py`
- `backend/tests/test_creative_provider_routing.py`

Important commits:

- `3d533fb9 Wire creative agents to provider routing`
- `8ce18e7d Guard Higgsfield live execution by video route`
- `e2dcbf08 Address creative provider routing review findings`

Result:

- Creative-capable agents now resolve through a single canonical routing layer instead of each flow making its own provider/model decision.
- Provider status metadata exposes Higgsfield and Nano Banana capabilities without exposing credential values.

## Higgsfield MCP, CLI, and Skill Context

The user clarified that Higgsfield had worked previously and that Higgsfield access could happen through MCP, CLI, or Skill.

What was established:

- Local Claude Code/Higgsfield MCP may help the operator workflow.
- The deployed Vantro backend still needs a server-side execution path with credentials or a deployable provider bridge.
- The provider routing layer does not store or expose Higgsfield secrets.
- The live backend still depends on configured production credentials/integrations for real provider execution.

Important note:

- The routing layer can select Higgsfield models correctly, but provider execution still requires working backend credentials and worker/provider infrastructure.

## GitHub, Vercel, and AWS Synchronization

The session repeatedly pushed changes to GitHub and verified Vercel production builds.

Vercel CLI work:

- Vercel CLI was installed globally.
- The usable Windows shim was:
  - `%APPDATA%\npm\vercel.cmd`
- Vercel deployments were inspected with `vercel ls` and `vercel inspect`.

Production deployment observations:

- Pushing to GitHub `main` triggered Vercel production deployments.
- Vercel aliases confirmed:
  - `https://vantro.ai`
  - `https://admin.vantro.ai`
  - `https://vantro-ai.vercel.app`

AWS workflow:

- `.github/workflows/deploy.yml` confirms that pushes to `main` are intended to build and deploy:
  - API image
  - worker image
  - agent worker image
  - ECS API service
  - ECS worker service
  - ECS agent worker service
- The workflow also runs Alembic migrations and post-deploy smoke tests.

Limitation:

- GitHub CLI was not authenticated locally.
- Direct AWS inspection was blocked later by the approval system due to workspace credit restrictions.
- Therefore, Vercel production state was directly verified, while AWS state had to be inferred from pushed commits and the configured workflow.

## Admin Run Proxy Debugging

The Create Media task repeatedly failed from the browser console.

Initial failing request:

- `/api/admin/agents/ugc_media_agent/run`
- Browser showed `500`.
- Vercel logs showed the request going through admin paths.

First proxy hardening:

- Added safer response forwarding for the dedicated admin agent route.
- Added safer response forwarding for the admin catch-all proxy.
- Added logging for proxy failures.

Commits:

- `730edb65 Safely forward admin agent run responses`
- `4dffeb2f Harden admin catch-all proxy responses`
- `d24ce2ca Expose admin proxy failure details`

Result:

- The proxy stopped trying to over-normalize backend responses.
- However, the browser still showed a 500, meaning the issue was deeper than frontend JSON parsing.

## Create Media Dedicated Proxy

To avoid the confusing dynamic admin proxy route, a new Vercel route was created:

`frontend/app/api/admin-run-agent/route.ts`

Create Media was updated to call:

`/api/admin-run-agent`

instead of:

`/api/admin/agents/{agentId}/run`

Commit:

- `179c106a Bypass admin run proxy for create media`

Tests added:

- `frontend/app/api/admin-run-agent/__tests__/route.test.ts`

Verified:

- New route tests passed.
- Admin proxy regression tests passed.
- Frontend production build passed.
- Vercel production deployment was `Ready`.

Result:

- The browser request moved from `/api/admin/agents/ugc_media_agent/run` to `/api/admin-run-agent`.
- This proved the old dynamic admin proxy path was no longer the frontend blocker.

## Backend Admin Workspace Bug

After the `/api/admin-run-agent` move, the frontend still received a 500. This showed that the backend itself was returning a server error.

Root cause found:

`backend/app/routes/admin.py` used fields that did not exist on the actual `Workspace` model:

- It queried `Workspace.owner_id`.
- It attempted to create `Workspace(plan="enterprise")`.

Actual model:

- `Workspace` is scoped by `organization_id`.
- `Workspace` requires `slug`.
- `Workspace` supports `workspace_type`, not `plan`.

Patch:

- Backend admin run route now resolves the admin organization first.
- It falls back to `Organization.owner_id == admin.id` when `admin.organization_id` is not populated.
- It creates an admin organization if needed.
- It creates an admin workspace using `organization_id`, `slug`, and `workspace_type`.

Commit:

- `bfc32edf Fix admin media job workspace resolution`

Regression test added:

- `backend/tests/test_admin_run_agent.py`

Limitation:

- Local backend pytest could not run because the Windows Python launcher pointed to a missing Python installation:
  - `C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe`
- The test remains committed for CI and future local environments with a working Python interpreter.

## Frontend Fallback for Admin Media Runs

After the backend patch, screenshots still showed `/api/admin-run-agent` returning 500. Since it was not possible to directly confirm whether AWS had deployed the backend patch, a defensive frontend fallback was added.

New behavior:

`/api/admin-run-agent` now tries:

1. `https://api.vantro.ai/api/admin/agents/{agentId}/run`
2. If that returns `5xx`, it falls back to:
   `https://api.vantro.ai/api/agents/{agentId}/run`

Reasoning:

- The standard `/api/agents/{id}/run` backend route already has admin detection and admin credit bypass.
- For admin users, it returns `enterprise` tier and skips credit checks.
- This route was already part of the normal production agent execution surface.

Commit:

- `a5d805f4 Fallback admin media runs to standard agent endpoint`

Tests added:

- Fallback test proving that a 500 from the admin backend route causes a second request to the standard agent endpoint.

Verified:

- Focused test suite:
  - `frontend/app/api/admin-run-agent/__tests__/route.test.ts`
  - 3 tests passed.
- Admin proxy regression set:
  - 3 suites passed.
  - 6 tests passed.
- Frontend production build passed.
- Vercel production deployment was `Ready`.
- Vercel production aliases included `https://admin.vantro.ai`.

Result:

- Create Media is no longer dependent on the backend admin route being healthy.
- It can fall back to the standard agent execution endpoint for admin users.

## Important Commits from This Session

- `3d533fb9 Wire creative agents to provider routing`
- `8ce18e7d Guard Higgsfield live execution by video route`
- `d26fdcac Fix root frontend build command`
- `e2dcbf08 Address creative provider routing review findings`
- `bcbc5a4a Show unlimited credits for admin dashboard`
- `730edb65 Safely forward admin agent run responses`
- `4dffeb2f Harden admin catch-all proxy responses`
- `d24ce2ca Expose admin proxy failure details`
- `179c106a Bypass admin run proxy for create media`
- `bfc32edf Fix admin media job workspace resolution`
- `a5d805f4 Fallback admin media runs to standard agent endpoint`

## Verification Completed

Frontend tests run and passed:

- `npm.cmd --prefix frontend test -- --runTestsByPath "app/api/admin-run-agent/__tests__/route.test.ts" --runInBand`
- `npm.cmd --prefix frontend test -- --runTestsByPath "app/api/admin-run-agent/__tests__/route.test.ts" "app/api/admin/[...path]/__tests__/route.test.ts" "app/api/admin/agents/[agentId]/run/__tests__/route.test.ts" --runInBand`

Frontend builds run and passed:

- `npm.cmd run build`

Vercel verification:

- Multiple production deployments were inspected.
- Final fallback deployment for commit `a5d805f4` was `Ready`.
- Aliases included `https://admin.vantro.ai` and `https://vantro.ai`.

Known warnings during build:

- Next.js inferred workspace root because multiple lockfiles exist.
- Middleware file convention is deprecated in favor of proxy.
- `frontend/app/api/auth/login/route.ts` exports a deprecated `config` object.

These warnings did not block the build.

## Current Known Limitations

1. Local Python test runner is broken on this machine.

   The local `pytest` launcher points to a missing Python path. Backend tests could not be executed locally until Python or the virtual environment is repaired.

2. AWS production verification was not directly completed from this session.

   The workflow exists, but direct AWS inspection was blocked by the tool approval system. Vercel was verified directly.

3. Higgsfield provider execution still depends on production credentials.

   Routing selects the intended Higgsfield and Nano Banana models. Actual generation requires valid backend provider credentials and worker execution.

4. Browser cache/service update can hide the latest frontend bundle.

   The Chrome UI showed "Relaunch to update". After Vercel deploys, the browser should be hard-refreshed or relaunched before retesting.

## Current Operational State

Public site:

- Canonical public landing site remains on `vantro.ai`.
- No prior public-site variant is part of the intended production surface.

Admin site:

- Canonical admin app lives at `admin.vantro.ai`.
- Admin Create Media route is `admin.vantro.ai/admin/create-media`.

Create Media:

- Frontend posts to `/api/admin-run-agent`.
- `/api/admin-run-agent` first tries the backend admin route.
- If that backend admin route returns `5xx`, it falls back to the standard agent route.

Creative routing:

- Higgsfield and Nano Banana model selection is centralized.
- Creative-capable agents resolve through canonical provider-routing logic.

Credits:

- Admin dashboard presents owner access as unlimited.
- Standard agent route skips credit checks for admins.

## Recommended Next Steps

1. Relaunch or hard-refresh Chrome and retry Create Media.

   Expected Network behavior:

   - Browser calls `/api/admin-run-agent`.
   - If backend admin route is still failing, the Vercel route falls back internally.
   - Browser should receive the fallback response from the standard agent route.

2. If Create Media still fails, inspect the response body for `/api/admin-run-agent`.

   The next useful evidence is the JSON body returned by that route, not just the browser console summary.

3. Repair local Python.

   This will allow backend regression tests to run locally again, especially:

   - `backend/tests/test_admin_run_agent.py`
   - `backend/tests/test_creative_provider_routing.py`

4. Confirm AWS workflow status from GitHub Actions or AWS Console.

   Specifically confirm whether commit `bfc32edf` or later is deployed to the ECS API service.

5. Confirm Higgsfield credentials in production.

   Provider routing is wired, but real video generation requires the backend/worker to have access to the required Higgsfield credential path.

## Locked-In Record

This report is intended as the durable session memory for the work completed on 2026-06-30. It records the domain decisions, admin route separation, landing-page cleanup, creative provider routing, Create Media proxy changes, backend admin workspace fix, fallback routing, verification performed, and remaining operational caveats.
