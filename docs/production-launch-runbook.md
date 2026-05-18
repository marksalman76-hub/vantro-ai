# Ecommerce AI Agent Platform — Final Production Launch Runbook

## Current Release State

The platform is in launch-candidate / pre-commercial-release state.

Confirmed:
- Frontend build passing
- Backend compile passing
- Durable media persistence installed
- Production storage adapter installed
- Stripe/billing runtime present
- Entitlement/commercial controls verified
- Client deliverable review UX installed
- Release lock passed

## Required Production Setup

### 1. Stripe Live Mode

Configure in production environment only:
- STRIPE_SECRET_KEY
- STRIPE_WEBHOOK_SECRET
- live price IDs for packages

Required live test:
1. Create a real test customer.
2. Start subscription checkout.
3. Confirm subscription active.
4. Confirm tenant/package activation.
5. Confirm failed payment policy is not shifting billing cycle.
6. Confirm cancellation respects month-to-month terms.

### 2. Production Media Storage

Recommended first option: Supabase Storage.

Configure:
- MEDIA_STORAGE_PROVIDER=supabase
- MEDIA_STORAGE_BUCKET
- MEDIA_STORAGE_PUBLIC_BASE_URL
- SUPABASE_URL
- SUPABASE_SERVICE_ROLE_KEY

Required test:
1. Prepare upload reference.
2. Upload one image.
3. Persist asset metadata.
4. Confirm latest deliverable returns image_url/download_url.
5. Confirm client portal renders asset.

### 3. Real Client Walkthrough

Run:
1. Create/activate client account.
2. Client logs in.
3. Client runs allowed agent.
4. Deliverable appears.
5. Client opens full deliverable modal.
6. Client approves.
7. Client rejects with feedback.
8. Client credit/package rules remain enforced.
9. Owner/admin remains unrestricted.

### 4. Deployment Monitoring

Before public traffic:
- uptime monitor on frontend
- uptime monitor on backend
- error logging
- backup verification
- rollback command verified
- production secrets checked
- no secrets committed to repo

## Known Non-Blocking Warning

Next.js middleware convention warning:
- migrate middleware to proxy later.
- currently non-blocking.
