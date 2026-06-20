# Stripe Webhook Testing Guide

## Overview
Local webhook testing allows you to test Stripe events without deploying to production.

## Setup Steps

### 1. Start Webhook Listener (Terminal 1)
```bash
cd backend
python stripe_webhook_listener.py
```

### 2. Forward Webhooks (Terminal 2)
```bash
npx stripe listen --forward-to localhost:8001/webhook
```

Copy the webhook secret and add to `.env`: