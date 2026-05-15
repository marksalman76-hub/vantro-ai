# Step 128 — Render Backend Setup Pack

Generated: 2026-05-14T14:57:12.669835+00:00

## Status

**Result:** Render backend setup pack created.  
**Completed steps:** `51-127`  
**Secret values included:** No

## Render Service Settings

| Item | Value |
|---|---|
| Provider | Render |
| Service type | Web Service |
| Runtime | Python |
| Environment | Production |

## Required Render Environment Variables

Add these only inside the Render dashboard.

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

## Optional Render Environment Variables

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

## Render Setup Steps

1. Create a new Render Web Service
2. Connect the GitHub repository
3. Select the ecommerce AI agent platform repository
4. Set runtime to Python
5. Set environment to production
6. Configure build command based on project requirements
7. Configure start command based on backend entry point
8. Add required environment variables in Render dashboard only
9. Deploy the service
10. Copy the live Render backend URL
11. Validate /health endpoint
12. Update non-secret live value record with backend URL

## Important Start/Build Command Note

Use the backend start/build command that matches the current project structure.  
If unsure, inspect the existing backend entry point before setting the Render command.

Do not guess the command if the project entry point is unclear.

## Safety Rules

- Do not paste Render env var values into source files.
- Do not commit `.env` files.
- Do not expose backend secrets to Vercel/frontend.
- Keep CORS locked to the Vercel production domain once the Vercel URL exists.
- Keep owner/admin and entitlement controls enabled.

## Release Decision

- Documentation can continue: `True`
- Live validation can continue: `False`
- Next step: Supabase database setup pack.
