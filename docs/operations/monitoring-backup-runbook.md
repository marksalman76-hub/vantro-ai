# Monitoring and Backup Operations Runbook

Draft operational runbook for launch readiness.

## Monitoring

Required production monitoring:
- Render backend uptime
- Vercel frontend uptime
- Stripe webhook delivery
- Database availability
- Critical API routes
- Failed execution events
- Billing failures
- Suspended/cancelled account events

## Critical Smoke Routes

Backend:
- /health
- /admin/billing/stripe-checkout-readiness
- /admin/deployment-control/summary
- /admin/deployment-control/list
- /run-agent

Frontend:
- /admin
- /admin-login
- /client
- /login
- /activate

## Backup Requirements

Required backup targets:
- Database backups
- Tenant/account records
- Billing state records
- Generated output records
- Deployment control state
- Legal/operations docs
- Environment variable inventory without secret values

## Alerting Requirements

Admin alerts should be created for:
- failed Stripe webhook
- failed checkout creation
- failed onboarding activation
- failed login spike
- failed execution
- credit gate blocks
- suspended/cancelled account attempt
- provider execution failure

## Recovery Requirements

Recovery should support:
- redeploy latest backend
- redeploy latest frontend
- restore database backup
- suspend affected tenant
- cancel affected tenant
- reactivate tenant after review
- manually deploy replacement tenant access
