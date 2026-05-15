# Step 113 — Backend Production Host Configuration Pack

Generated: 2026-05-14T14:11:00.993658+00:00

## Status

**Result:** Backend production host configuration pack created.  
**Secret values included:** No

## Backend Service Requirements

| Item | Value |
|---|---|
| Runtime | Python |
| Recommended host | Render / Railway / Fly.io / AWS / GCP / Azure |
| Environment | Production |
| Health endpoint | `/health` |

## Required Backend Environment Variables

Add these only inside the backend deployment provider dashboard.

- `APP_ENV`
- `BACKEND_URL`
- `FRONTEND_URL`
- `DATABASE_URL`
- `JWT_SECRET`
- `ADMIN_AUTH_SECRET`
- `OWNER_ADMIN_EMAIL`
- `OPENAI_API_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`

## Optional Backend Environment Variables

Add only if the related provider/integration is enabled.

- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`
- `XAI_API_KEY`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `FROM_EMAIL`
- `SHOPIFY_API_KEY`
- `SHOPIFY_API_SECRET`
- `META_ADS_ACCESS_TOKEN`
- `TIKTOK_ADS_ACCESS_TOKEN`
- `KLAVIYO_API_KEY`

## Recommended Backend Deployment Settings

| Setting | Value |
|---|---|
| Root directory | Project root or backend directory depending on provider |
| Python version | Use current project-compatible Python version |
| Build command | Install backend dependencies |
| Start command | Start backend API server |
| Health check path | `/health` |
| Auto deploy | Optional for release candidate; recommended after stable production setup |

## Backend Deployment Safety Rules

- Do not commit `.env` files with real values.
- Do not paste backend secrets into frontend variables.
- Do not expose provider credentials to client/browser runtime.
- Keep owner/admin routes protected.
- Keep production CORS restricted to the production frontend URL.
- Keep all approval/governance controls enabled.

## Release Decision

- Can continue: `True`
- Next step: Frontend production host configuration pack.
