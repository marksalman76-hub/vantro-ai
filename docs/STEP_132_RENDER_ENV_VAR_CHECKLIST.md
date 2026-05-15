# Step 132 — Render Environment Variable Checklist

Generated: 2026-05-14T15:01:48.751641+00:00

## Status

**Result:** Render environment variable checklist created.  
**Completed steps:** `51-131`  
**Secret values included:** No

## Required Render Environment Variables

| Variable | Purpose |
|---|---|
| `APP_ENV` | production |
| `BACKEND_URL` | Render backend URL after deploy |
| `FRONTEND_URL` | Vercel frontend URL after deploy |
| `DATABASE_URL` | Supabase Postgres connection string - enter in Render only |
| `JWT_SECRET` | Generate/store in Render only |
| `ADMIN_AUTH_SECRET` | Generate/store in Render only |
| `OWNER_ADMIN_EMAIL` | Owner/admin notification email |
| `OPENAI_API_KEY` | OpenAI key - enter in Render only |
| `STRIPE_SECRET_KEY` | Stripe secret key - enter in Render only |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret - enter in Render only |

## Optional Render Environment Variables

| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Optional fallback LLM key |
| `GOOGLE_API_KEY` | Optional fallback LLM key |
| `XAI_API_KEY` | Optional fallback LLM key |
| `SMTP_HOST` | Optional email provider host |
| `SMTP_PORT` | Optional email provider port |
| `SMTP_USER` | Optional email provider username |
| `SMTP_PASSWORD` | Optional email provider password - enter in Render only |
| `FROM_EMAIL` | Optional sender email |
| `SHOPIFY_API_KEY` | Optional ecommerce integration |
| `SHOPIFY_API_SECRET` | Optional ecommerce integration secret - enter in Render only |
| `META_ADS_ACCESS_TOKEN` | Optional ad integration token - enter in Render only |
| `TIKTOK_ADS_ACCESS_TOKEN` | Optional ad integration token - enter in Render only |
| `KLAVIYO_API_KEY` | Optional email/SMS integration key - enter in Render only |

## Forbidden Locations For Secrets

- GitHub repository
- local committed .env files
- Vercel frontend env vars for backend secrets
- docs
- screenshots
- chat
- client/browser runtime

## Render Env Var Rules

- Backend secrets go in Render only.
- Supabase `DATABASE_URL` goes in Render only.
- OpenAI and Stripe secret keys go in Render only.
- Do not put backend secrets in Vercel.
- Do not commit real `.env` files.
- Do not paste secret values into chat or screenshots.
- `FRONTEND_URL` should be updated after the Vercel production URL exists.
- CORS must be locked to the final Vercel production URL.

## Release Decision

- Documentation can continue: `True`
- Live validation can continue: `False`
- Next step: Create Vercel env var checklist for selected stack.
