# Soft Launch Pilot Checklist

## Pilot Setup
- Create one demo/admin-controlled client.
- Create one real pilot customer account.
- Confirm customer package and active agents.
- Confirm Stripe checkout page opens for the selected package.
- Confirm customer can log in.
- Confirm customer can see only active paid agents.

## Execution Validation
- Run one admin/internal multi-agent execution.
- Run one customer execution after credit/subscription readiness.
- Confirm output is client-safe.
- Confirm execution is stored.
- Confirm blocked execution messaging works when credits are exhausted.

## Billing Validation
- Confirm Stripe readiness.
- Confirm checkout session creation.
- Confirm webhook monitoring is active.
- Confirm cancellation/reactivation controls.

## Support Validation
- Confirm support email/contact flow.
- Confirm admin issue tracking process.
- Confirm suspended/cancelled account escalation flow.

## Launch Decision
Soft launch is approved when:
- At least one pilot customer completes onboarding.
- At least one checkout flow reaches Stripe successfully.
- At least one execution flow succeeds.
- Admin can suspend/cancel/reactivate.
- No secrets are exposed in frontend or API responses.
