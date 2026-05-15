# Step 130 — Vercel Frontend Setup Pack

Generated: 2026-05-14T14:59:09.531019+00:00

## Status

**Result:** Vercel frontend setup pack created.  
**Completed steps:** `51-129`  
**Secret values included:** No

## Vercel Settings

| Item | Value |
|---|---|
| Provider | Vercel |
| Environment | Production |
| Required live dependency | Render backend URL |

## Required Public Frontend Environment Variables

Only client-safe public/config values may be added in Vercel.

- `FRONTEND_URL`
- `BACKEND_URL`
- `STRIPE_PUBLISHABLE_KEY`

## Forbidden Vercel Environment Variables

Never add these to Vercel/frontend runtime.

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
- `Supabase service role key`
- `database password`
- `any private token`

## Required Vercel Actions

1. Create/import Vercel project
2. Connect GitHub repository
3. Select frontend root directory
4. Configure public frontend environment variables only
5. Set BACKEND_URL to Render backend URL after Render deploy
6. Deploy Vercel frontend
7. Copy Vercel production frontend URL
8. Add Vercel production frontend URL to Render backend CORS allowlist
9. Validate homepage route
10. Validate admin route
11. Validate client route
12. Validate frontend-to-backend API communication

## Vercel Safety Rules

- Do not add backend secrets to Vercel.
- Do not add database credentials to Vercel.
- Do not expose LLM, Stripe secret, SMTP, JWT, admin, or Supabase service role keys.
- Customer portal must not expose internal prompts, agent logic, learning logic, governance rules, or backend configuration.
- Admin dashboard may show operational state, but must not expose secrets.
- Vercel production URL must be added to Render backend CORS allowlist.

## Release Decision

- Documentation can continue: `True`
- Live validation can continue: `False`
- Next step: Render/Vercel/Supabase external setup sequence.
