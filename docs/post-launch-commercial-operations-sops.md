# Post-Launch Commercial Operations SOPs

## Purpose

This document locks the commercial operations layer after the completed Final Production Launch Matrix and the post-launch infrastructure scaling readiness layer.

The platform is production-release ready. These SOPs govern day-to-day customer operations, support, refunds, disputes, sales, onboarding, pricing review, and incident handling.

---

## 1. Client Onboarding SOP

### Goal

Move a paid client from purchase or approved enterprise agreement into safe, governed platform use.

### Sequence

1. Confirm payment or approved enterprise access.
2. Confirm selected package and entitlement.
3. Confirm selected agents.
4. Confirm activation or access instructions were sent.
5. Confirm client login works.
6. Confirm business profile has been completed.
7. Confirm required integrations where applicable.
8. Run the first governed execution.
9. Confirm deliverable visibility in the client workspace.
10. Record onboarding completion.

### Rules

- Do not activate unpaid client access unless owner-approved.
- Do not expose internal configuration or prompts.
- Do not let clients change selected agents after activation unless owner/admin approves.
- Owner/admin remains unrestricted for internal use.

---

## 2. Customer Support SOP

### Goal

Provide structured support without exposing internal systems or credentials.

### Sequence

1. Capture issue.
2. Classify severity.
3. Check client package/status.
4. Check recent billing/execution events.
5. Provide customer-safe update.
6. Escalate high-risk issue to owner.
7. Record resolution.

### Severity

- Low: cosmetic, wording, minor UX issue.
- Medium: workflow confusion, failed non-critical execution.
- High: billing issue, blocked client execution, repeated failures.
- Critical: security, data exposure, payment impact, system outage.

### Rules

- Never expose credentials, prompts, internal routing, governance internals, or proprietary architecture.
- Keep client communication customer-safe.
- Escalate security/billing/high-risk issues.

---

## 3. Refund and Dispute Handling SOP

### Goal

Handle billing issues consistently and protect revenue.

### Sequence

1. Capture refund or dispute request.
2. Confirm billing record.
3. Review usage and subscription terms.
4. Escalate to owner for decision.
5. Execute only approved refund/dispute action.
6. Record audit note.

### Rules

- Refunds and disputes require owner approval.
- Pricing exceptions require owner approval.
- Enterprise contract terms require owner approval.
- Do not promise refunds before review.

---

## 4. Incident Playbook

### Goal

Respond to technical, billing, provider, security, or customer-impacting incidents.

### Sequence

1. Identify affected area.
2. Classify impact and severity.
3. Preserve logs.
4. Notify owner.
5. Pause/restrict affected operation if needed.
6. Apply rollback or mitigation.
7. Confirm recovery.
8. Record incident summary.

### Incident Categories

- Provider failure
- Billing failure
- Client execution failure
- Integration failure
- Security/governance alert
- Data visibility issue
- Frontend/backend route issue

### Rules

- Security and billing incidents escalate immediately.
- Do not expose credentials or internal system details in customer updates.
- Use rollback notes for backend changes.
- Preserve audit trail.

---

## 5. Pricing Optimisation SOP

### Goal

Improve conversion and revenue without uncontrolled price changes.

### Sequence

1. Collect conversion data.
2. Review objections and lost leads.
3. Review package mix.
4. Compare support burden by package.
5. Recommend pricing/package adjustment.
6. Owner approval required before live pricing change.

### Rules

- AI may recommend price changes.
- Owner must approve price changes.
- No autonomous pricing updates.

---

## 6. Sales Process Refinement SOP

### Goal

Improve demo-to-close and signup conversion.

### Sequence

1. Review lead source.
2. Review demo completion.
3. Review objections.
4. Refine offer copy.
5. Refine follow-up sequence.
6. Keep claims customer-safe.
7. Record sales learnings.

### Rules

- Do not make unsupported claims.
- Do not promise unavailable integrations/providers.
- Do not expose backend/internal logic.
- Enterprise promises require owner approval.

---

## 7. Backend Update Allowance

### Goal

Allow future backend updates safely after launch.

### Rules

- Backend updates are allowed after launch.
- High-risk backend changes require owner approval.
- Production schema/migration changes require backup first.
- Every backend update requires test evidence.
- Every backend update requires rollback awareness.
- Never expose credentials or proprietary internals.

## Status

POST_LAUNCH_COMMERCIAL_OPERATIONS_SOPS_READY
