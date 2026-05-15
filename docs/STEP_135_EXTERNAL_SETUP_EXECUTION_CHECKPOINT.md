# Step 135 — External Setup Execution Checkpoint

Generated: 2026-05-14T15:05:36.139949+00:00

## Status

**Result:** External setup execution checkpoint created.  
**Completed steps:** `51-134`  
**Secret values included:** No

## Selected Stack

| Layer | Provider |
|---|---|
| Backend | Render |
| Frontend | Vercel |
| Database | Supabase |
| Llm | OpenAI |
| Payments | Stripe |

## External Execution Order

1. Create Supabase project
2. Copy Supabase DATABASE_URL into Render only
3. Create Render backend Web Service
4. Configure Render required env vars
5. Deploy Render backend
6. Confirm Render backend /health URL
7. Create Vercel frontend project
8. Configure Vercel public env vars only
9. Deploy Vercel frontend
10. Copy Vercel frontend URL into Render FRONTEND_URL
11. Lock Render CORS to Vercel frontend URL
12. Redeploy/restart Render backend
13. Run live validation command pack

## Manual Inputs Needed Next

- Render live backend URL
- Vercel live frontend URL
- Supabase project created confirmation
- Render env vars configured confirmation
- Vercel public env vars configured confirmation

## Current Release Decision

| Decision | Value |
|---|---:|
| Documentation can continue | `True` |
| External setup can begin | `True` |
| Live validation can continue | `False` |
| Production release can be approved | `False` |

## Next Action

Start external provider setup with Supabase first.

## Secret Rule

Do not paste Supabase, Render, Vercel, OpenAI, Stripe, JWT, admin, SMTP, or database secret values into this repository, docs, screenshots, chat, or frontend variables.
