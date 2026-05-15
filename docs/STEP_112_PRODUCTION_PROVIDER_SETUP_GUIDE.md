# Step 112 — Production Provider Setup Guide

Generated: 2026-05-14T14:10:12.305207+00:00

## Status

**Result:** Production provider setup guide created.  
**Completed steps:** `51-111`  
**Secret values included:** No

## Correct Setup Order

1. Backend host
2. Database provider
3. Frontend host
4. LLM provider credentials
5. Stripe configuration
6. Email notification provider
7. Domain/DNS
8. CORS/security hardening
9. Live endpoint validation
10. Final release approval

## Backend Host

Use Render, Railway, Fly.io, AWS, GCP, or Azure.

Required items:

- Production service created
- Project/repository connected
- Build command configured
- Start command configured
- Environment variables added in provider dashboard only
- Health endpoint `/health` verified
- Logs reviewed after first deploy

## Database Provider

Use a managed Postgres provider such as Render Postgres, Supabase, Neon, Railway Postgres, AWS RDS, or equivalent.

Required items:

- Production database created
- `DATABASE_URL` configured in backend host dashboard
- Backup policy enabled
- Restore process documented
- Database access not exposed publicly without security controls

## Frontend Host

Use Vercel, Netlify, Cloudflare Pages, or equivalent.

Required items:

- Frontend app deployed
- Production backend API URL configured
- Admin route verified
- Client/customer route verified
- HTTPS enabled
- No internal backend secrets added to frontend environment variables

## LLM Provider Credentials

Required items:

- OpenAI key configured in backend deployment dashboard
- Optional fallback provider keys configured only if used
- No LLM keys stored in repository
- Live LLM readiness endpoint tested after deployment
- Live execution remains owner-governed where required

## Stripe

Required items:

- Stripe mode selected: test or live
- Publishable key configured where frontend requires it
- Secret key configured only in backend/provider dashboard
- Webhook secret configured only in backend/provider dashboard
- Success/cancel URLs configured
- Webhook delivery tested

## Email Notification Provider

Required items:

- SMTP/API provider selected
- Sender email/domain verified
- Owner notification email configured
- Delivery test completed
- Credentials stored only in provider dashboard

## Domain/DNS

Required items:

- Frontend domain configured
- Backend/API domain configured if using custom API domain
- DNS records set correctly
- HTTPS/TLS active
- Redirects checked
- No mixed-content errors

## CORS / Security

Required items:

- CORS locked to production frontend domain
- JWT secret configured
- Admin auth secret configured
- Owner/admin access protected
- Client access does not expose internal logic
- Provider credentials never exposed to client/browser

## Final Rule

Do not paste production secrets into source code, docs, GitHub, screenshots, or chat.

## Release Decision

- Can continue: `True`
- Next step: Backend production host configuration pack.
