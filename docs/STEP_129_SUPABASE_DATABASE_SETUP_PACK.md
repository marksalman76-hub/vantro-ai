# Step 129 — Supabase Database Setup Pack

Generated: 2026-05-14T14:58:11.774240+00:00

## Status

**Result:** Supabase database setup pack created.  
**Completed steps:** `51-128`  
**Secret values included:** No

## Supabase Settings

| Item | Value |
|---|---|
| Provider | Supabase |
| Database type | Postgres |
| Required Render env var | `DATABASE_URL` |

## Required Supabase Actions

1. Create a Supabase project
2. Select a secure region close to target users or backend host
3. Create/confirm production database
4. Copy database connection string only into Render DATABASE_URL
5. Enable SSL connection where required
6. Confirm backups are enabled according to selected Supabase plan
7. Keep Supabase service role keys out of frontend runtime
8. Do not expose database credentials in repository files
9. Document non-secret project name/region only if needed
10. Run backend database connectivity validation after Render deploy

## Forbidden Frontend Values

Never add these to Vercel/frontend variables.

- `DATABASE_URL`
- `Supabase service role key`
- `database password`
- `direct Postgres connection string`

## Supabase Safety Rules

- `DATABASE_URL` belongs in Render backend environment variables only.
- Supabase service role keys must never be exposed to client/browser runtime.
- Do not commit database credentials.
- Do not paste database credentials into chat or screenshots.
- Production and test data should remain separated.
- Backup/restore policy must be confirmed before final production approval.

## Release Decision

- Documentation can continue: `True`
- Live validation can continue: `False`
- Next step: Vercel frontend setup pack.
