# Step 114 — Frontend Production Host Configuration Pack

Generated: 2026-05-14T14:11:58.375781+00:00

## Status

**Result:** Frontend production host configuration pack created.  
**Secret values included:** No

## Frontend Service Requirements

| Item | Value |
|---|---|
| Recommended host | Vercel / Netlify / Cloudflare Pages |
| Environment | Production |
| Required routes | `/`, `/admin`, `/client` |

## Required Public Frontend Environment Variables

Only public/client-safe values may be configured in the frontend host.

- `FRONTEND_URL`
- `BACKEND_URL`
- `STRIPE_PUBLISHABLE_KEY`

## Forbidden Frontend Environment Variables

Do not add backend secrets, provider secrets, database URLs, admin secrets, or LLM keys to the frontend host.

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

## Required Frontend Routes

- `/`
- `/admin`
- `/client`

## Frontend Deployment Safety Rules

- Frontend must not expose internal prompts, agent logic, learning architecture, governance internals, backend routes, or secret configuration.
- Client portal must remain customer-safe and must not show raw internal IDs, secret names, backend config, or execution internals.
- Admin dashboard can show operational status, but not raw provider secrets.
- Frontend API calls must target the production backend URL only.
- Production frontend URL must be added to backend CORS allowlist.
- HTTPS must be enabled.

## Release Decision

- Can continue: `True`
- Next step: Database production configuration pack.
