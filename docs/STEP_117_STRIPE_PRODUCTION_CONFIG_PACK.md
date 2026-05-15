# Step 117 — Stripe Production Configuration Pack

Generated: 2026-05-14T14:32:58.763614+00:00

## Status

**Result:** Stripe production configuration pack created.  
**Secret values included:** No

## Provider

Stripe

## Required Backend Environment Variables

Configure only inside backend deployment/provider dashboard.

- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`

## Required Frontend Public Environment Variables

Configure only in frontend host if checkout/client display requires it.

- `STRIPE_PUBLISHABLE_KEY`

## Required Stripe Dashboard Configuration

- products/packages created
- prices created
- checkout success URL configured
- checkout cancel URL configured
- webhook endpoint configured
- webhook events selected
- test mode verified before live mode
- live mode enabled only after owner approval

## Required Webhook Events

- `checkout.session.completed`
- `invoice.payment_succeeded`
- `invoice.payment_failed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`

## Required Production Validation

- checkout session can be created
- successful payment activates correct package/entitlements
- failed payment blocks or suspends access correctly
- cancelled subscription downgrades or suspends access correctly
- webhook signature verification works
- client cannot activate unpaid features
- owner/admin can see billing status safely

## Stripe Safety Rules

- Do not commit Stripe secret keys.
- Do not add `STRIPE_SECRET_KEY` or `STRIPE_WEBHOOK_SECRET` to frontend variables.
- Use test mode before live mode.
- Enable live mode only after owner approval.
- Entitlements must activate only after verified successful payment.
- Failed/cancelled payments must block, downgrade, or suspend access according to package rules.
- Clients must not be able to activate unpaid agents, credits, packages, or features.

## Release Decision

- Can continue: `True`
- Next step: Email notification production configuration pack.
