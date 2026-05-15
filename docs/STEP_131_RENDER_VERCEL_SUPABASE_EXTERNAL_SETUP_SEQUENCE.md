# Step 131 — Render / Vercel / Supabase External Setup Sequence

Generated: 2026-05-14T15:00:32.867120+00:00

## Status

**Result:** External setup sequence created.  
**Completed steps:** `51-130`  
**Secret values included:** No

## Selected Stack

| Layer | Provider |
|---|---|
| Backend | Render |
| Frontend | Vercel |
| Database | Supabase |
| Llm | OpenAI |
| Payments | Stripe |

## Recommended Setup Sequence

1. Create Supabase project first
2. Copy Supabase database connection string into Render DATABASE_URL only
3. Create Render backend web service
4. Configure Render backend env vars
5. Deploy Render backend
6. Confirm Render /health endpoint
7. Create Vercel frontend project
8. Set Vercel BACKEND_URL to Render backend URL
9. Deploy Vercel frontend
10. Copy Vercel production URL
11. Update Render FRONTEND_URL and CORS allowlist to Vercel production URL
12. Redeploy/restart Render backend after CORS update
13. Run Step 122 live deployment validation command pack

## Blocked Until

- Supabase project exists
- Render backend service exists
- Vercel frontend project exists
- Render backend URL is available
- Vercel frontend URL is available
- CORS locked to Vercel production URL
- Step 122 live validation passes

## Critical Order Rule

Create and connect Supabase before finalising Render because Render needs the Supabase `DATABASE_URL`.

Deploy Render before finalising Vercel because Vercel needs the Render `BACKEND_URL`.

After Vercel is deployed, update Render with the final Vercel `FRONTEND_URL` and CORS allowlist.

## Secret Handling Rule

Do not paste database URLs, API keys, Stripe secrets, JWT secrets, admin secrets, or SMTP passwords into files, docs, screenshots, GitHub, frontend variables, or chat.

## Release Decision

- Documentation can continue: `True`
- Live validation can continue: `False`
- Next step: Create Render env var checklist for selected stack.
