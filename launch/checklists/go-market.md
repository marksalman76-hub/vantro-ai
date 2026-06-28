# Vantro.ai Go-to-Market Launch Checklist

**Solo founder:** Mark Salman (mark.salman76@gmail.com)
**Stack:** FastAPI backend · Next.js 16 frontend · PostgreSQL (migration head: 021) · 27 AI agents · AWS ECS/Fargate target

---

## 1. Stripe Configuration

- [ ] Stripe account switched to **live mode** — confirm at dashboard.stripe.com (top-left toggle shows "Live")
- [ ] Live publishable key `pk_live_...` set in frontend env: `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` (Vercel env vars or `.env.production`)
- [ ] Live secret key `sk_live_...` stored in AWS Secrets Manager as `vantro/production/stripe-secret-key` (not in `.env` file)
- [ ] Webhook endpoint registered in Stripe dashboard → Developers → Webhooks: `https://api.vantro.ai/api/stripe/webhook`
- [ ] Webhook events subscribed (all six required):
  - [ ] `customer.subscription.created`
  - [ ] `customer.subscription.updated`
  - [ ] `customer.subscription.deleted`
  - [ ] `invoice.payment_succeeded`
  - [ ] `invoice.payment_failed`
  - [ ] `checkout.session.completed`
- [ ] `STRIPE_WEBHOOK_SECRET` (`whsec_...`) stored in Secrets Manager as `vantro/production/stripe-webhook-secret`; verify it matches the signing secret shown in Stripe dashboard for the registered endpoint
- [ ] Stripe Products created and Price IDs stored as env vars:
  - [ ] Starter Monthly → `STRIPE_STARTER_MONTHLY_PRICE_ID=price_...`
  - [ ] Starter Annual → `STRIPE_STARTER_ANNUAL_PRICE_ID=price_...`
  - [ ] Growth Monthly → `STRIPE_GROWTH_MONTHLY_PRICE_ID=price_...`
  - [ ] Growth Annual → `STRIPE_GROWTH_ANNUAL_PRICE_ID=price_...`
  - [ ] Business Monthly → `STRIPE_BUSINESS_MONTHLY_PRICE_ID=price_...`
  - [ ] Business Annual → `STRIPE_BUSINESS_ANNUAL_PRICE_ID=price_...`
  - [ ] Enterprise → contact-sales flow (no Stripe price ID required)
- [ ] Stripe Customer Portal enabled: dashboard.stripe.com → Settings → Billing → Customer portal → Activate; configure allowed actions (plan change, cancellation, payment method update)
- [ ] Test checkout end-to-end with a live card (Stripe test card does NOT work in live mode — use a real card with $0.50 minimum or Stripe's live test card for real accounts): register → select Starter → Stripe Checkout → `checkout.session.completed` webhook fires → `CreditsAccount.balance` updated in DB
  ```sql
  SELECT ca.balance, ca.tier FROM credits_accounts ca
  JOIN workspaces w ON w.id = ca.workspace_id
  WHERE w.name = '<test-workspace-name>';
  ```
- [ ] Failed payment handling verified: trigger `invoice.payment_failed` via Stripe dashboard test event → confirm `stripe_webhook_handler.py` locks workspace or downgrades tier; verify workspace cannot run paid-tier agents after lock
- [ ] `live_stripe_bridge_runtime.py` and `stripe_checkout_runtime.py` both reference live-mode Price IDs (no `price_test_` prefixes)
- [ ] `stripe_customer_billing_portal.py` Customer Portal session uses live-mode Stripe customer IDs

---

## 2. Pricing Page

- [ ] Pricing page live at `https://vantro.ai/pricing` (HTTP 200, not redirect loop)
- [ ] Page loads in <3s — run: `npx lighthouse https://vantro.ai/pricing --only-categories=performance --output=json | jq '.categories.performance.score'` → must be ≥ 0.7
- [ ] Starter tier: lists all agents where `min_package = "starter"` in `AGENT_CATALOGUE`; shows credit allocation for starter subscription
- [ ] Growth tier: lists additional agents where `min_package = "growth"`; shows incremental credit allocation
- [ ] Business tier: lists agents where `min_package = "business"` (e.g., Strategist Agent, Business Growth & Partnerships Agent); shows business credit allocation
- [ ] Enterprise tier: shows "Contact us" or custom flow — no hard-coded Stripe Price ID exposed in page source
- [ ] Annual pricing discount (if applicable) displayed and mathematically correct (verify against Stripe price amounts)
- [ ] "Get started" / "Start free" CTA routes to `/register` (not `/login`)
- [ ] Upgrade CTA on each tier routes to Stripe Checkout with correct `price_id`
- [ ] No frontend references to provider/model names — run: `grep -r "claude\|anthropic\|gpt\|openai" frontend/` → must return 0 results in user-visible files (`.tsx`, `.ts`, `.js`, `.json` inside `app/`)
- [ ] Pricing page has correct `<title>` and meta description for SEO

---

## 3. Onboarding Flow

Test the complete new user journey end-to-end with a real email address:

- [ ] Register at `/register` with real email (e.g., `mark+onboard-test@vantro.ai`)
- [ ] Activation email received within 60s — check subject line reads correctly, from address is `noreply@vantro.ai` or `hello@vantro.ai` (not `localhost`)
- [ ] Activation token in email works:
  ```
  curl -s "https://api.vantro.ai/api/auth/activate?token=<TOKEN>" | jq '.message'
  ```
  Expected: `"Account activated successfully"` (or equivalent)
- [ ] Post-activation: account row in `activation_tokens` table marked used:
  ```sql
  SELECT used, used_at FROM activation_tokens WHERE token = '<TOKEN>';
  ```
- [ ] Login at `/login` → JWT issued, stored in HTTP-only cookie (verify in DevTools → Application → Cookies → no JWT visible in JS-accessible storage)
- [ ] Redirect to dashboard (`/dashboard`) after successful login
- [ ] Workspace auto-created on first login OR workspace creation modal appears — confirm workspace row exists:
  ```sql
  SELECT id, name, created_at FROM workspaces WHERE owner_id = '<user_id>' LIMIT 1;
  ```
- [ ] `CreditsAccount` row created for workspace with correct starting balance for tier:
  ```sql
  SELECT balance, tier FROM credits_accounts WHERE workspace_id = '<workspace_id>';
  ```
- [ ] First agent run: select a starter-tier agent (e.g., Research Agent), submit prompt → job row appears:
  ```sql
  SELECT id, status, agent_id, created_at FROM agent_jobs
  WHERE workspace_id = '<workspace_id>' ORDER BY created_at DESC LIMIT 1;
  ```
  Status transitions: `pending` → `running` → `completed` (within 90s for HITL-0 agents)
- [ ] Credits deducted after job completion:
  ```sql
  SELECT credits_used, output FROM agent_jobs WHERE id = '<job_id>';
  ```
  `credits_used` must be > 0; `output` must be non-null
- [ ] Job output displayed in dashboard UI — no raw JSON, no stack traces visible to user
- [ ] Job rating/feedback UI works: submit a 1-5 star rating → `rating` column updated on `agent_jobs` row:
  ```sql
  SELECT rating FROM agent_jobs WHERE id = '<job_id>';
  ```
- [ ] `CreditsAccount.balance` reduced by `credits_used`:
  ```sql
  SELECT balance FROM credits_accounts WHERE workspace_id = '<workspace_id>';
  ```

---

## 4. Admin Portal

- [ ] Admin portal accessible at `/admin` when logged in as `mark.salman76@gmail.com` — HTTP 200
- [ ] Admin portal NOT accessible to regular users: login as any non-admin user → navigate to `/admin` → verify HTTP 403 or redirect to `/dashboard` (must not render admin UI)
  ```
  curl -s -H "Cookie: <non-admin-session-cookie>" https://vantro.ai/admin -o /dev/null -w "%{http_code}"
  ```
  Expected: `403` or `302`
- [ ] HITL-3 (`pending_approval`) job queue visible in admin portal with approve/reject actions
- [ ] `pending_financial_review` queue visible and filterable by workspace, date, agent
- [ ] Workspace list shows workspace names, credit balances, subscription tiers
- [ ] Manual credit top-up works: select workspace → add N credits → verify `CreditsAccount.balance` updated:
  ```sql
  SELECT balance FROM credits_accounts WHERE workspace_id = '<workspace_id>';
  ```
- [ ] Organization and workspace creation from admin portal creates correct DB rows (org → workspace → credits_account chain)
- [ ] Agent job history searchable/filterable by `workspace_id`, `agent_id`, `status` — results correct
- [ ] Skill RAG manual re-index: `POST https://api.vantro.ai/api/admin/skills/index` (with admin auth) returns 200; `OPENAI_API_KEY` must be set in production env for this to do anything
  ```
  curl -s -X POST https://api.vantro.ai/api/admin/skills/index \
    -H "Authorization: Bearer <admin-token>" | jq '.status'
  ```
- [ ] Announcements/changelog: admin can POST new announcement (migration `020_announcements_changelog_status.py`) → announcement appears in user-facing dashboard
  ```sql
  SELECT id, title, published_at FROM announcements ORDER BY created_at DESC LIMIT 3;
  ```

---

## 5. Email & Notifications

- [ ] Transactional email provider configured: verify `EMAIL_HOST` (SMTP) or AWS SES region/identity set in Secrets Manager as `vantro/production/email-config`
- [ ] SES sending identity `vantro.ai` verified in AWS SES console (or SMTP provider sender domain verified)
- [ ] Welcome/activation email sends on registration: register test account → email received within 60s with correct activation link pointing to `https://vantro.ai/...` (not `localhost:3000`)
- [ ] From address is `noreply@vantro.ai` or `hello@vantro.ai` — not `user@localhost`, not `no-reply@example.com`
- [ ] Financial review alert: run an agent that triggers `scan_for_financial_actions` match → `mark.salman76@gmail.com` receives alert email with job ID and matched phrase
- [ ] HITL-3 approval request: submit a HITL-3 agent (e.g., Head Agent) → `mark.salman76@gmail.com` receives approval request email with direct link or job ID
- [ ] Password reset flow:
  ```
  curl -s -X POST https://api.vantro.ai/api/auth/forgot-password \
    -H "Content-Type: application/json" \
    -d '{"email": "mark+resettest@vantro.ai"}' | jq '.message'
  ```
  → reset email received → reset link works → `POST /api/auth/reset-password` with token sets new password → login with new password succeeds
- [ ] SPF record set for `vantro.ai`:
  ```
  nslookup -type=TXT vantro.ai
  ```
  Must include `v=spf1 include:amazonses.com ~all` (or your provider's include)
- [ ] DKIM record set: check AWS SES → Verified Identities → `vantro.ai` → DKIM status = "Verified"
- [ ] DMARC record set:
  ```
  nslookup -type=TXT _dmarc.vantro.ai
  ```
  Must return a valid DMARC record (e.g., `v=DMARC1; p=quarantine; rua=mailto:dmarc@vantro.ai`)
- [ ] Send test email through real provider and verify not in spam: use [mail-tester.com](https://www.mail-tester.com) → score ≥ 8/10

---

## 6. Legal & Compliance

- [ ] Terms of Service live at `https://vantro.ai/terms` (HTTP 200, substantive content — not placeholder)
- [ ] Privacy Policy live at `https://vantro.ai/privacy` (HTTP 200, covers data collection, retention, and AI processing disclosure)
- [ ] Cookie consent banner active (migration `018_cookie_consent.py`): visit `https://vantro.ai` in incognito → banner appears → accepting/rejecting updates `cookie_consent` table:
  ```sql
  SELECT consent_given, given_at, ip_hash FROM cookie_consent ORDER BY created_at DESC LIMIT 5;
  ```
- [ ] GDPR: user data deletion endpoint documented or implemented (e.g., `DELETE /api/user/me` or admin-triggered purge); confirm process in Privacy Policy
- [ ] No client-visible references to underlying model/provider names:
  ```
  grep -ri "claude\|anthropic\|openai\|gpt-\|haiku\|sonnet\|opus" frontend/app/ frontend/components/ frontend/lib/
  ```
  Must return 0 matches in any `.tsx`, `.ts`, `.js` files that render to the client
- [ ] `/api/docs` and `/api/redoc` return 404 in production (OpenAPI disabled):
  ```
  curl -s -o /dev/null -w "%{http_code}" https://api.vantro.ai/api/docs
  curl -s -o /dev/null -w "%{http_code}" https://api.vantro.ai/api/redoc
  ```
  Both must return `404`
- [ ] `Server` response header stripped: `curl -I https://api.vantro.ai/health | grep -i server` → must return nothing or `server: (empty)` (SecurityHeadersMiddleware active)
- [ ] AI-generated content disclosure: if required by jurisdiction or Stripe/AWS ToS, add disclosure that outputs are AI-generated

---

## 7. Domain & SSL

- [ ] `vantro.ai` resolves and returns HTTP 200:
  ```
  curl -s -o /dev/null -w "%{http_code}" https://vantro.ai
  ```
- [ ] `api.vantro.ai` resolves to backend ALB and health check passes:
  ```
  curl -s https://api.vantro.ai/health | jq '.status'
  ```
  Expected: `"ok"` or `"healthy"`
- [ ] SSL certificate valid for `vantro.ai` and `api.vantro.ai` — no browser warnings:
  ```
  curl -I https://vantro.ai 2>&1 | head -5
  curl -I https://api.vantro.ai 2>&1 | head -5
  ```
  Must show `HTTP/2 200`, no SSL error
- [ ] SSL certificate expiry > 60 days:
  ```
  echo | openssl s_client -servername vantro.ai -connect vantro.ai:443 2>/dev/null | openssl x509 -noout -dates
  ```
- [ ] `www.vantro.ai` redirects to `vantro.ai` (301):
  ```
  curl -s -o /dev/null -w "%{http_code}" https://www.vantro.ai
  ```
  Expected: `301` with `Location: https://vantro.ai/`
- [ ] No mixed content warnings: open `https://vantro.ai` in Chrome → DevTools → Console → no "Mixed Content" errors
- [ ] HSTS header present:
  ```
  curl -I https://vantro.ai | grep -i strict-transport
  ```
  Expected: `strict-transport-security: max-age=...`

---

## 8. Pre-Launch Smoke Tests

Run these manually the day before launch. All must pass before go-live.

- [ ] **Full registration → first agent run:**
  Register `mark+smoketest@vantro.ai` → activation email received → activate → login → workspace created → run Research Agent (HITL-0, `min_package=starter`) with prompt `"What are the top e-commerce trends in 2026?"` → job completes within 90s → output present in dashboard → credits deducted

- [ ] **HITL-3 approval flow:**
  Submit Head Agent job (HITL-3) → job status = `pending_approval` in DB:
  ```sql
  SELECT status FROM agent_jobs WHERE agent_id = 'head_agent' ORDER BY created_at DESC LIMIT 1;
  ```
  → Admin notification email received → approve in `/admin` → job executes to `completed`

- [ ] **Cross-workspace isolation:**
  Create two separate organizations/workspaces (Org A, Org B) → attempt to call `GET /api/agents/jobs` from Org A session with Org B's `workspace_id` in query → must return `403` or empty list (no cross-tenant data leak):
  ```
  curl -s "https://api.vantro.ai/api/agents/jobs?workspace_id=<ORG_B_WORKSPACE_ID>" \
    -H "Authorization: Bearer <ORG_A_TOKEN>" | jq '.total'
  ```
  Expected: `403` or `{"total": 0, "jobs": []}`

- [ ] **Package gate enforcement:**
  On starter workspace, attempt to run a `min_package=business` agent (e.g., `strategist_agent`) → must return 403 or upgrade prompt — job must NOT be created in DB:
  ```
  curl -s -X POST https://api.vantro.ai/api/agents/strategist_agent/run \
    -H "Authorization: Bearer <STARTER_WORKSPACE_TOKEN>" \
    -H "Content-Type: application/json" \
    -d '{"task": "test"}' | jq '.detail'
  ```

- [ ] **Stripe Growth checkout:**
  Complete purchase of Growth plan → `checkout.session.completed` webhook visible in Stripe dashboard event log → `CreditsAccount` tier updated to `growth` in DB:
  ```sql
  SELECT tier, balance FROM credits_accounts WHERE workspace_id = '<workspace_id>';
  ```

- [ ] **Stripe cancellation:**
  Cancel subscription via Customer Portal → `customer.subscription.deleted` webhook fires (visible in Stripe event log) → workspace reverts to starter tier:
  ```sql
  SELECT tier FROM credits_accounts WHERE workspace_id = '<workspace_id>';
  ```

- [ ] **OpenAPI disabled in production:**
  ```
  curl -s -o /dev/null -w "%{http_code}" https://api.vantro.ai/docs
  curl -s -o /dev/null -w "%{http_code}" https://api.vantro.ai/redoc
  ```
  Both must return `404` — if either returns `200`, set `ENVIRONMENT=production` and redeploy immediately

- [ ] **Financial output scan:**
  Submit agent job with task containing financial trigger phrase (e.g., "approve a $500 spend") → job routed to `pending_financial_review` (not `completed`):
  ```sql
  SELECT status, financial_flag FROM agent_jobs WHERE id = '<job_id>';
  ```
  → `mark.salman76@gmail.com` receives financial review alert email

- [ ] **Suspicious path blocking:**
  ```
  curl -s -o /dev/null -w "%{http_code}" https://api.vantro.ai/.env
  curl -s -o /dev/null -w "%{http_code}" https://api.vantro.ai/wp-admin
  curl -s -o /dev/null -w "%{http_code}" "https://api.vantro.ai/api/../../../etc/passwd"
  ```
  All must return `400` or `404` (security_hardening_runtime.py scanner active)

- [ ] **Skill RAG operational:**
  POST to skill index endpoint → check that `skill_chunks` table has rows:
  ```sql
  SELECT COUNT(*) FROM skill_chunks;
  ```
  Must be > 0 (requires `OPENAI_API_KEY` set in production)

- [ ] **Agent catalogue count intact:**
  ```
  curl -s https://api.vantro.ai/api/admin/agents \
    -H "Authorization: Bearer <ADMIN_TOKEN>" | jq '.total'
  ```
  Must return `27` — if not, `AGENT_CATALOGUE` has been modified without approval

---

*Last updated: 2026-06-28 — Mark Salman, solo founder*
