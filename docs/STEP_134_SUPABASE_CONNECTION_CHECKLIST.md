# Step 134 — Supabase Connection Checklist

Generated: 2026-05-14T15:04:15.249237+00:00

## Status

**Result:** Supabase connection checklist created.  
**Completed steps:** `51-133`  
**Secret values included:** No

## Supabase Connection Rules

| Rule | Value |
|---|---|
| Database Provider | `Supabase` |
| Database Type | `Postgres` |
| Render Env Var | `DATABASE_URL` |
| Vercel Allowed | `False` |
| Frontend Exposure Allowed | `False` |
| Service Role Frontend Allowed | `False` |

## Required Supabase Checks

- Supabase project created
- Supabase project region selected
- Production database available
- Connection string copied only into Render DATABASE_URL
- Database SSL requirement confirmed
- Supabase service role key kept out of Vercel/frontend
- Database password not stored in repository
- Backups/restore policy confirmed
- Production and test data separation confirmed
- Render backend can connect to Supabase after deployment

## Forbidden Locations For Database Credentials

- Vercel environment variables
- frontend runtime
- GitHub repository
- docs
- screenshots
- chat
- client/browser runtime
- committed .env files

## Supabase Safety Rules

- `DATABASE_URL` must be entered in Render only.
- Vercel must not receive Supabase database credentials.
- Supabase service role key must never be exposed to frontend/client runtime.
- Database passwords and direct connection strings must not be committed, screenshotted, or pasted into chat.
- Backend connectivity must be verified after Render deployment.
- Backup and restore readiness must be confirmed before final release approval.

## Release Decision

- Documentation can continue: `True`
- Live validation can continue: `False`
- Next step: Create external setup execution checkpoint.
