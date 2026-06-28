# Legal & Compliance Launch Checklist — Vantro.ai

_Last updated: 2026-06-28 | Owner: mark.salman76@gmail.com_
_All items must be checked before production traffic is enabled._

---

## 1. Terms of Service & Privacy Policy

- [ ] Terms of Service published at `https://vantro.ai/legal/terms`
- [ ] Privacy Policy published at `https://vantro.ai/legal/privacy`
- [ ] Both documents linked in site footer on every page (including authenticated app)
- [ ] Documents are versioned: current version number and effective date are displayed at top of each document (e.g. `v1.0 — Effective 2026-07-01`)
- [ ] Effective date is set **before** first paid customer signs up (not retroactive)
- [ ] Acceptance is captured at signup: checkbox `I agree to the Terms of Service and Privacy Policy` with links — stored in DB (`users.tos_accepted_at`, `users.tos_version`)
- [ ] Verify acceptance stored:
  ```sql
  SELECT email, tos_accepted_at, tos_version FROM users
  WHERE tos_accepted_at IS NULL AND created_at < NOW()
  LIMIT 10;
  -- Must return 0 rows for any real production user
  ```
- [ ] Material changes trigger re-acceptance gate (bump `tos_version`, check at login)
- [ ] ToS explicitly covers: multi-tenant data isolation, credit consumption model, agent output disclaimer (AI-generated content is not advice), HITL-3 manual approval disclosure

---

## 2. Cookie Consent

- [ ] Cookie consent banner visible to all unauthenticated visitors before any non-essential cookies fire
- [ ] Categories implemented and disclosed:
  - [ ] **Strictly necessary** (session, CSRF) — no consent required
  - [ ] **Functional** (preferences, language) — opt-in or legitimate interest documented
  - [ ] **Analytics** (e.g. PostHog, Plausible) — explicit opt-in required for EU/UK visitors
  - [ ] **Marketing** (retargeting pixels) — explicit opt-in required for EU/UK visitors
- [ ] Consent state is stored server-side or in a first-party cookie (not only localStorage)
- [ ] "Reject all" option is as prominent as "Accept all" (GDPR Article 7 + EDPB guidance)
- [ ] Consent log: timestamp, IP (hashed), consent version, categories accepted — retained for 3 years
- [ ] Cookie banner does NOT fire after consent is already given (no re-prompt on every page load)
- [ ] Cookie policy page lists every cookie name, purpose, expiry, and first/third-party classification

---

## 3. GDPR / Data Subject Rights

- [ ] Data deletion endpoint implemented and tested:
  ```bash
  # Verify deletion cascades through org → workspace → jobs → credits
  curl -X DELETE https://vantro.ai/api/admin/users/{user_id}/gdpr-erase \
    -H "Authorization: Bearer $ADMIN_TOKEN"
  # Expected: 200 with {"status": "queued", "estimated_completion": "..."}
  ```
- [ ] Deletion covers: user PII, workspace data, agent job inputs/outputs, credit history (aggregate totals may be retained for accounting)
- [ ] Data export (portability) endpoint returns machine-readable JSON/CSV of all user data
- [ ] Retention policy documented in Privacy Policy:
  - Active data: retained while account active
  - Job inputs/outputs: 90 days after job completion (configurable per workspace)
  - Billing records: 7 years (legal requirement)
  - Audit logs: 1 year
- [ ] Retention policy is actually enforced — scheduled job purges stale records:
  ```sql
  -- Verify old job payloads are being purged
  SELECT COUNT(*) FROM agent_jobs
  WHERE completed_at < NOW() - INTERVAL '91 days'
    AND input_payload IS NOT NULL;
  -- Should be 0 if purge job is running
  ```
- [ ] DPA (Data Processing Agreement) template drafted and available for EU/EEA customers on request
- [ ] Privacy Policy names data controller (Mark Salman / Vantro.ai entity) and EU representative if applicable
- [ ] Sub-processor list is current (see Section 4)
- [ ] Data subject request contact: `privacy@vantro.ai` or in-app form
- [ ] Response SLA for data subject requests: 30 days (GDPR Article 12)

---

## 4. Data Processing & Sub-Processors

- [ ] Sub-processor list published (linked from Privacy Policy):
  | Sub-processor | Purpose | Location | Transfer mechanism |
  |---|---|---|---|
  | Amazon Web Services | Hosting, compute, storage | US (primary), EU optional | SCCs / adequacy |
  | Stripe | Payment processing | US | SCCs |
  | AI provider (unnamed) | Agent inference | US | SCCs |
  | Email provider (e.g. Resend/SES) | Transactional email | US | SCCs |
- [ ] AI provider is listed generically as "AI inference provider" — **no mention of Anthropic, OpenAI, claude-*, gpt-* in any client-facing document**
- [ ] Standard Contractual Clauses (SCCs) or equivalent in place for any EU data transferred to US processors
- [ ] AWS data residency: confirm which regions customer data is stored in; disclose in Privacy Policy
- [ ] Stripe: no raw card data ever touches Vantro servers — only Stripe tokens/payment method IDs
- [ ] Internal data access: only `mark.salman76@gmail.com` (admin) can access workspace data; logged in audit table

---

## 5. Tech Stack Opacity Compliance

- [ ] Run grep across all API response models to ensure no provider names leak:
  ```bash
  grep -rE "claude|anthropic|openai|gpt-|haiku|sonnet|opus" \
    backend/app/api/ backend/app/models/ backend/app/schemas/ \
    --include="*.py" -l
  # Must return 0 files
  ```
- [ ] Run grep across frontend code:
  ```bash
  grep -rE "claude|anthropic|openai|gpt-|haiku|sonnet|opus" \
    frontend/app/ frontend/components/ \
    --include="*.tsx" --include="*.ts" --include="*.js" -l
  # Must return 0 files (except internal comments in .env.example which is never shipped)
  ```
- [ ] Error messages tested — no model names in 4xx/5xx responses:
  ```bash
  # Trigger a bad request and check response body
  curl -s -X POST https://vantro.ai/api/agents/invalid_id/run \
    -H "Authorization: Bearer $TEST_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"task": "test"}' | python3 -m json.tool
  # Must not contain: claude, anthropic, openai, gpt, haiku, sonnet, opus, fastapi, sqlalchemy
  ```
- [ ] `Server` response header is stripped (SecurityHeadersMiddleware active):
  ```bash
  curl -sI https://vantro.ai/api/health | grep -i server
  # Must return nothing (or generic value like "vantro")
  ```
- [ ] OpenAPI docs disabled in production:
  ```bash
  curl -s -o /dev/null -w "%{http_code}" https://vantro.ai/docs
  curl -s -o /dev/null -w "%{http_code}" https://vantro.ai/redoc
  curl -s -o /dev/null -w "%{http_code}" https://vantro.ai/openapi.json
  # All must return 404
  ```
- [ ] `ENVIRONMENT=production` confirmed in ECS task definition environment variables
- [ ] Log streams (CloudWatch) are not accessible to clients and do not appear in API error bodies

---

## 6. Provider Agreements

- [ ] Anthropic Terms of Service reviewed for commercial/SaaS use case — usage is compliant
- [ ] OpenAI Terms of Service reviewed for commercial/SaaS use case — usage is compliant (embeddings/RAG)
- [ ] Both provider agreements allow reselling AI capabilities as part of a SaaS product (confirm no output ownership clauses conflict with customer deliverables)
- [ ] Vantro ToS includes AI output disclaimer consistent with both provider ToS requirements
- [ ] Provider API keys stored in AWS Secrets Manager — not in environment variables or code
- [ ] Auto-rotation schedule set for provider API keys (or calendar reminder for manual rotation)

---

## 7. Stripe Compliance

- [ ] Stripe live mode enabled and confirmed (not test mode in production)
  ```bash
  # Check Stripe key prefix — must be sk_live_ in production
  aws secretsmanager get-secret-value --secret-id vantro/stripe_secret_key \
    --query SecretString --output text | python3 -c "import sys; k=sys.stdin.read().strip(); print('LIVE' if k.startswith('sk_live_') else 'TEST — FAIL')"
  ```
- [ ] Webhook endpoint configured in Stripe Dashboard pointing to `https://vantro.ai/api/billing/webhook`
- [ ] Webhook signature verification active in code — `stripe.Webhook.construct_event()` with `STRIPE_WEBHOOK_SECRET`
- [ ] Stripe.js / Payment Element used in frontend — **no raw card numbers ever sent to Vantro backend**
- [ ] PCI scope confirmed as SAQ A (card data handled entirely by Stripe, not Vantro)
- [ ] Stripe Customer Portal enabled for self-serve subscription management
- [ ] Refund policy matches what Stripe Customer Portal allows (see Section 10)
- [ ] Subscription cancellation handled: workspace downgraded, credits not refunded for partial periods (or document exception)
- [ ] Failed payment retry logic configured in Stripe (Smart Retries enabled)
- [ ] Dunning email sequence active in Stripe (payment failed → 3-day retry → account suspension warning)

---

## 8. Email Compliance

- [ ] Every transactional email contains:
  - [ ] Physical mailing address (CAN-SPAM requirement)
  - [ ] Unsubscribe link for non-essential emails (account alerts may be exempt as transactional)
  - [ ] Sender name is "Vantro" — not a personal name or misleading header
- [ ] Marketing emails (launch announcements, feature updates) require prior consent — separate opt-in from account creation
- [ ] Unsubscribe requests honored within 10 business days (CAN-SPAM); immediately for GDPR
- [ ] Email sending domain (`vantro.ai`) has SPF, DKIM, and DMARC records set:
  ```bash
  nslookup -type=TXT vantro.ai | grep "v=spf"
  nslookup -type=TXT _dmarc.vantro.ai | grep "v=DMARC"
  # Both must return valid records
  ```
- [ ] Bounce and complaint handling configured in SES/Resend — suppression list enforced
- [ ] Admin notifications (financial_review queue, HITL-3 approval) sent to `mark.salman76@gmail.com` — not a client-visible address

---

## 9. Accessibility

- [ ] WCAG 2.1 Level AA compliance targeted for all public-facing pages: `/`, `/pricing`, `/signup`, `/login`, `/onboarding`
- [ ] Automated scan run with Axe or Lighthouse:
  ```bash
  npx axe https://vantro.ai/pricing --reporter=cli
  # Target: 0 critical violations, 0 serious violations
  ```
- [ ] Colour contrast ratio >= 4.5:1 for all body text, 3:1 for large text
- [ ] All interactive elements reachable and operable via keyboard only
- [ ] Form fields have visible labels (not just placeholder text)
- [ ] Images have descriptive `alt` attributes; decorative images have `alt=""`
- [ ] Focus indicators visible on all focusable elements
- [ ] `<html lang="en">` set on all pages
- [ ] Pricing page: plan comparison table has proper `<th scope>` and ARIA labels
- [ ] Agent catalogue page: card list uses `<ul>/<li>` or equivalent ARIA role

---

## 10. Security

- [ ] SAST scan run on Python backend:
  ```bash
  cd backend
  pip install bandit
  bandit -r app/ -ll -f txt
  # Target: 0 HIGH severity findings
  ```
- [ ] Dependency vulnerability scan — Python:
  ```bash
  cd backend
  pip install pip-audit
  pip-audit --require-hashes -r requirements.txt
  # All CRITICAL and HIGH CVEs must be resolved before launch
  ```
- [ ] Dependency vulnerability scan — Node:
  ```bash
  cd frontend
  npm audit --audit-level=high
  # 0 high/critical vulnerabilities
  ```
- [ ] Penetration test or third-party security review completed (or scheduled within 60 days of launch)
- [ ] Security findings log: all findings documented with severity, owner, and remediation date
- [ ] `INJECTION_GUARD` block confirmed present in all system prompts — verified in `agent_executor.py`
- [ ] `scan_for_financial_actions` active and tested: submit a job containing "make a payment" and confirm it routes to `pending_financial_review`
- [ ] Rate limiting active on all auth routes (10/min) and agent execution routes
- [ ] Suspicious path scanner active (`app/core/security_hardening_runtime.py`) — test:
  ```bash
  curl -s -o /dev/null -w "%{http_code}" https://vantro.ai/.env
  curl -s -o /dev/null -w "%{http_code}" https://vantro.ai/wp-admin
  # Both must return 403 or 404
  ```
- [ ] All secrets in AWS Secrets Manager — no secrets in `.env` files committed to git:
  ```bash
  git log --all --full-history -- .env "*.env" | head -5
  grep -rE "sk_live_|FERNET_KEY|SECRET_KEY" .git/  2>/dev/null | wc -l
  # Must be 0
  ```
- [ ] `HTTPS` enforced everywhere — HTTP redirects to HTTPS (ALB listener rule)
- [ ] HSTS header set: `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- [ ] `X-Frame-Options: DENY` and `X-Content-Type-Options: nosniff` headers present

---

_Completed by: _____________ Date: _____________ Sign-off: mark.salman76@gmail.com_
