# Customer-Ready Launch Checklist — Vantro.ai

_Last updated: 2026-06-28 | Owner: mark.salman76@gmail.com_
_All items must be checked before first paying customer is onboarded._

---

## 1. Support Infrastructure

- [ ] Help desk tool selected and configured (e.g. Linear, Intercom, Freshdesk, Plain)
- [ ] `support@vantro.ai` email alias created and routes to help desk inbox
- [ ] Help desk notifications go to `mark.salman76@gmail.com` until team scales
- [ ] Response SLA defined and published:
  | Priority | Criteria | Target response |
  |---|---|---|
  | P1 — Critical | Service down, data loss risk, billing error blocking access | < 4 hours |
  | P2 — High | Agent failures, HITL-3 stuck, credits depleted unexpectedly | < 24 hours |
  | P3 — Normal | Feature questions, onboarding help, billing clarifications | < 3 business days |
  | P4 — Low | General feedback, enhancement requests | Best effort |
- [ ] SLA is documented in ToS or SLA annex (starter tier may have P3-only SLA)
- [ ] On-call alert configured: P1 tickets trigger SMS/push to `mark.salman76@gmail.com`
- [ ] Help desk linked from in-app "Help" button and footer

---

## 2. Onboarding Documentation

- [ ] Getting Started guide written and published (docs.vantro.ai or Notion/GitBook):
  - [ ] Create organization → workspace flow explained with screenshots
  - [ ] How to connect integrations (Composio) explained
  - [ ] How to run your first agent (step-by-step with expected output)
  - [ ] Credit system explained: what credits are, cost per agent, how to top up
- [ ] Agent catalogue documented — all 27 agents listed with:
  - [ ] Agent name and one-sentence description
  - [ ] What inputs it expects
  - [ ] What output it produces
  - [ ] Credit cost estimate (HITL level noted where relevant)
  - [ ] Which tier(s) can access it (starter / growth / business / enterprise)
- [ ] HITL-3 approval flow documented for enterprise customers: "Some high-impact agents require owner approval before running. You will receive an email when approval is needed."
- [ ] Credit system page explains:
  - Starter: X credits/month included
  - Growth: Y credits/month included
  - Top-up pricing per 1,000 credits
  - Credits expire policy (if any)
  - How to view usage in dashboard

---

## 3. In-App Onboarding

- [ ] New workspace empty state handled — not a blank page:
  - [ ] Welcome banner with user's name
  - [ ] "Run your first agent" CTA visible
  - [ ] Agent catalogue link prominent
- [ ] First agent run is guided:
  - [ ] Suggested agent surfaced based on workspace type (or general suggestion)
  - [ ] Input field has placeholder text / example task
  - [ ] Post-run: result shown clearly, credit deduction displayed, "run another" CTA
- [ ] Trial / signup credits automatically applied on workspace creation:
  ```sql
  -- Verify new workspaces get trial credits
  SELECT w.name, ca.balance, ca.created_at
  FROM workspaces w
  JOIN credits_accounts ca ON ca.workspace_id = w.id
  WHERE w.created_at > NOW() - INTERVAL '1 day'
  ORDER BY w.created_at DESC;
  -- balance should be > 0 for all new workspaces if trial credits are enabled
  ```
- [ ] Zero-credit state handled gracefully: clear message "You've used all your credits — top up to continue" with billing CTA, not a cryptic error
- [ ] Package gate message is clear when user tries to access an agent above their tier: "This agent requires the Growth plan. Upgrade to unlock."
- [ ] HITL-3 pending state shown in UI: "This job is awaiting owner approval" with timestamp

---

## 4. Knowledge Base / FAQ

- [ ] Knowledge base live at `docs.vantro.ai` or equivalent (Intercom Articles / Notion / GitBook)
- [ ] Top 10 anticipated questions answered:
  - [ ] "What is Vantro and what can it do?"
  - [ ] "What are credits and how do they work?"
  - [ ] "Why did my agent job fail?"
  - [ ] "How do I connect my tools (CRM, email, Slack)?"
  - [ ] "What is the difference between the plans?"
  - [ ] "Can I get a refund if I don't use all my credits?"
  - [ ] "Is my data secure? Who can see my workspace data?"
  - [ ] "Why is my job stuck in 'pending approval'?"
  - [ ] "How do I add team members to my workspace?"
  - [ ] "Can I export agent outputs?"
- [ ] Billing FAQ covers:
  - [ ] When am I charged (monthly cycle date)?
  - [ ] What happens when I run out of credits mid-month?
  - [ ] Can I downgrade my plan? When does it take effect?
  - [ ] How do I cancel? Will I lose my data immediately?
- [ ] Agent failure FAQ covers:
  - [ ] Common failure reasons (missing integration credentials, task too vague, rate limits)
  - [ ] How to retry a failed job
  - [ ] How to contact support for persistent failures
  - [ ] What "pending financial review" means and what to expect

---

## 5. Support Team Training (Owner Self-Briefing)

- [ ] HITL-3 approval flow understood end-to-end:
  - Job submitted → status `pending_approval` → email to `mark.salman76@gmail.com` → navigate to admin portal → approve/reject → worker picks up
  - Verify: `GET /api/admin/jobs?status=pending_approval` returns correct jobs
- [ ] Financial review queue understood:
  - `scan_for_financial_actions` matches → job status `pending_financial_review` → admin email sent
  - Review job output in admin portal, decide to release or reject
  - Verify queue:
    ```bash
    curl -s https://vantro.ai/api/admin/jobs?status=pending_financial_review \
      -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool
    ```
- [ ] Manual credit top-up procedure documented:
  ```bash
  # Top up 500 credits for a workspace
  curl -X POST https://vantro.ai/api/admin/workspaces/{workspace_id}/credits/topup \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"amount": 500, "reason": "Support goodwill credit"}'
  ```
- [ ] How to impersonate a workspace for debugging (if implemented) — procedure documented and access logged
- [ ] Escalation path if a job is stuck and cannot be resolved: DB-level status reset procedure documented in `launch/runbooks/`

---

## 6. First-Use Email Sequence

- [ ] Welcome email (T+0, immediate on signup):
  - [ ] Sent from `hello@vantro.ai` or `mark@vantro.ai`
  - [ ] Includes: trial credit balance, link to "Run your first agent", link to docs
  - [ ] Tested in both plain-text and HTML rendering
  - [ ] Unsubscribe link present (CAN-SPAM compliant)
- [ ] Day-3 check-in email (T+72h if user has NOT run an agent):
  - [ ] Subject: "Have you tried Vantro yet?" or equivalent
  - [ ] Single suggested agent with one concrete use-case example
  - [ ] Link to Getting Started guide
  - [ ] Triggered only if `agent_jobs` count for workspace = 0 at T+72h
- [ ] Day-7 "try this agent" nudge (T+7d):
  - [ ] Highlights 1-2 agents matched to signup intent (if captured) or most popular agents
  - [ ] Shows remaining trial credits if on trial
  - [ ] Soft CTA to upgrade if credits are running low
- [ ] Email sequence confirmed NOT sending to users who have already converted to paid (suppress on `subscription_status = active`)
- [ ] All emails render correctly tested in: Gmail (web), Apple Mail, Outlook 365

---

## 7. Error Message Audit

- [ ] All 4xx responses are generic — no stack traces, no internal paths, no model names:
  ```bash
  # Test 422 validation error
  curl -s -X POST https://vantro.ai/api/agents/research_agent/run \
    -H "Authorization: Bearer $TEST_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{}' | python3 -m json.tool
  # Must not contain: traceback, sqlalchemy, fastapi, claude, anthropic, /app/, /usr/

  # Test 401 unauthorized
  curl -s https://vantro.ai/api/agents/ \
    -H "Authorization: Bearer invalid_token" | python3 -m json.tool
  # Must return: {"detail": "Not authenticated"} or equivalent — nothing internal

  # Test 404
  curl -s https://vantro.ai/api/agents/nonexistent_agent_id/run \
    -H "Authorization: Bearer $TEST_TOKEN" | python3 -m json.tool
  # Must return generic "Agent not found" — not the DB query or model name
  ```
- [ ] 500 errors return generic message only:
  ```bash
  grep -r "traceback\|exc_info\|raise\|Exception" backend/app/api/ --include="*.py" -l
  # Confirm no raw exception propagation to HTTP responses
  ```
- [ ] Agent job failure reason stored internally but surfaced to client as generic:
  ```sql
  -- Confirm error_detail column exists and is not exposed in API schema
  SELECT column_name FROM information_schema.columns
  WHERE table_name = 'agent_jobs' AND column_name = 'error_detail';
  -- Then confirm it's excluded from the public job response schema
  ```
- [ ] Financial review / pending approval messages shown to clients are generic: "Your job requires additional review before processing" — no mention of what triggered it
- [ ] Credential test endpoint (`/api/integrations/{id}/test`) returns pass/fail only — not the decrypted credential or the specific auth error from the third-party service

---

## 8. Feedback Loop

- [ ] In-app feedback widget installed (e.g. Typeform embed, Intercom, or custom):
  - [ ] Accessible from every page via persistent "Feedback" button or help menu
  - [ ] Captures: rating (1-5), free text, current page URL, workspace ID (for context)
  - [ ] Submissions route to `mark.salman76@gmail.com` or help desk
- [ ] Post-agent-run feedback prompt implemented: "Was this result useful? 👍 👎" logged to `agent_job_feedback` table
- [ ] NPS survey scheduled at T+14 days for all active users:
  - [ ] "On a scale of 0-10, how likely are you to recommend Vantro to a colleague?"
  - [ ] Open text follow-up on score
  - [ ] Sent via email or in-app (not both — choose one to avoid fatigue)
- [ ] Feedback data reviewed weekly by owner — schedule a recurring calendar reminder

---

## 9. Status Page

- [ ] Status page live at `https://status.vantro.ai` (Instatus, Statuspage.io, or BetterUptime)
- [ ] Components monitored and displayed:
  - [ ] API (`api.vantro.ai`)
  - [ ] Web app (`app.vantro.ai`)
  - [ ] Agent worker / job processing
  - [ ] Database
  - [ ] Billing / Stripe integration
- [ ] "Subscribe to updates" link on status page (email + RSS)
- [ ] Subscribe link in site footer and in support email signatures
- [ ] Incident template ready (fill in and post within 15 minutes of P1 detection):
  ```
  **[INVESTIGATING]** We are aware of an issue affecting [component].
  Impact: [what users experience]
  Started: [HH:MM UTC]
  Next update: [HH:MM UTC]
  ```
- [ ] Post-incident: root cause analysis posted within 48 hours for any P1 incident
- [ ] Status page URL referenced in ToS under "Service Availability" section
- [ ] CloudWatch alarm → SNS → status page auto-update configured (or manual update process documented in `launch/runbooks/incident-response.md`)

---

## 10. Cancellation & Refund Policy

- [ ] Cancellation policy written and published:
  - Cancellation takes effect at end of current billing period
  - No partial-month refunds on subscription fees (credits consumed are non-refundable)
  - Exception: first 14 days — full refund if no agent jobs completed (document any variation)
- [ ] Policy linked from:
  - [ ] Pricing page
  - [ ] Checkout / upgrade flow
  - [ ] Account → Billing page
  - [ ] Cancellation confirmation email
- [ ] Stripe Customer Portal enabled and configured:
  - [ ] Customers can cancel self-serve (no email-to-cancel dark pattern)
  - [ ] Customers can view invoices and download receipts
  - [ ] Customers can update payment method
  - [ ] Customer portal URL: `https://billing.stripe.com/p/login/...` linked from `app.vantro.ai/settings/billing`
- [ ] Cancellation triggers:
  - [ ] Confirmation email sent immediately with effective date
  - [ ] Workspace downgraded at period end (not immediately)
  - [ ] Data retention notice sent: "Your data will be retained for 30 days after cancellation, then permanently deleted"
- [ ] Refund issuance process documented for support team:
  ```bash
  # Issue refund via Stripe API (for goodwill/exception cases)
  # stripe refunds create --charge=ch_xxx --amount=5000
  # Amount in cents; always confirm with customer before issuing
  ```
- [ ] Chargeback / dispute handling: Stripe Radar enabled, evidence template ready (login logs, job completion records, email correspondence)

---

_Completed by: _____________ Date: _____________ Sign-off: mark.salman76@gmail.com_
