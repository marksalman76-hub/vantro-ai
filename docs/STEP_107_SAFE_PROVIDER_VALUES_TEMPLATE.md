# Step 107 — Safe Provider Values Template

Generated: 2026-05-14T14:04:50.563063+00:00

## Status

**Result:** Safe provider values template created.  
**Secret values included:** No  
**Safe to use as checklist:** Yes  
**Safe to store real secrets here:** No

## Provider Checklist

| Provider Layer | Status |
|---|---|
| Backend host | Pending |
| Frontend host | Pending |
| Database provider | Pending |
| LLM provider stack | Pending |
| Payment provider | Pending |
| Email notification provider | Pending |
| Domain/DNS provider | Pending |

## Required Secret Fields

Do not paste real values into this repository.

- `DATABASE_URL`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`
- `XAI_API_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `SMTP_PASSWORD`

## Required Public / Config Fields

- `BACKEND_URL`
- `FRONTEND_URL`
- `STRIPE_PUBLISHABLE_KEY`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `FROM_EMAIL`
- `APP_ENV=production`

## Release Decision

- Can continue: `True`
- Real provider values must be configured only inside Render/Vercel/provider dashboards, not committed to source code.

## Next Step

Production readiness matrix update.
