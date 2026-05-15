# Step 133 — Vercel Environment Variable Checklist

Generated: 2026-05-14T15:02:46.000692+00:00

## Status

**Result:** Vercel environment variable checklist created.  
**Completed steps:** `51-132`  
**Secret values included:** No

## Allowed Vercel Public Environment Variables

Only these public/client-safe values are allowed in Vercel.

| Variable | Purpose |
|---|---|
| `FRONTEND_URL` | Vercel production frontend URL |
| `BACKEND_URL` | Render production backend URL |
| `STRIPE_PUBLISHABLE_KEY` | Stripe public publishable key only |

## Forbidden Vercel Environment Variables

Never add these to Vercel or frontend runtime.

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`
- `XAI_API_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `DATABASE_URL`
- `JWT_SECRET`
- `ADMIN_AUTH_SECRET`
- `SMTP_PASSWORD`
- `SHOPIFY_API_SECRET`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_DB_PASSWORD`
- `any private API key`
- `any database connection string`
- `any backend-only token`

## Required Vercel Checks

- Vercel FRONTEND_URL points to the deployed frontend URL
- Vercel BACKEND_URL points to the Render backend URL
- No backend secrets exist in Vercel env vars
- No database credentials exist in Vercel env vars
- Customer portal does not expose internal logic
- Admin dashboard does not expose raw secrets
- Frontend successfully calls Render backend after deployment
- Render CORS allows the Vercel production URL only

## Vercel Env Var Rules

- Vercel must only receive frontend-safe public/config values.
- Render receives backend secrets.
- Supabase database credentials stay in Render only.
- OpenAI/Stripe secret/JWT/admin secrets stay in Render only.
- Client portal must not expose internal prompts, learning logic, provider routing, governance rules, backend configuration, or secrets.
- Admin dashboard may show safe operational state only.

## Release Decision

- Documentation can continue: `True`
- Live validation can continue: `False`
- Next step: Create Supabase connection checklist for selected stack.
