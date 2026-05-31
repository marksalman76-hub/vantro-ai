# Live Production Provisioning Checklist

## Owner-controlled actions

Do not paste secrets into chat or commit them to Git.

### Render backend required secrets
- ADMIN_PLATFORM_TOKEN
- JWT_SECRET
- SESSION_SECRET
- DATABASE_URL
- OPENAI_API_KEY
- STRIPE_SECRET_KEY
- STRIPE_WEBHOOK_SECRET
- SMTP_PASSWORD
- BREVO_API_KEY
- SUPABASE_SERVICE_ROLE_KEY

### Vercel frontend required secrets
- ADMIN_PLATFORM_TOKEN
- SESSION_SECRET

### Supabase required secrets
- DATABASE_URL
- SUPABASE_SERVICE_ROLE_KEY

## Required before enabling live execution
1. Rotate production secrets directly inside provider dashboards.
2. Store rollback values securely outside the repository.
3. Add new values to Render/Vercel/Supabase environment settings.
4. Redeploy backend and frontend after environment updates.
5. Run the controlled activation verifier.
6. Only then approve low-volume live execution.
