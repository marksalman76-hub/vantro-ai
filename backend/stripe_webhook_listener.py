"""
Stripe Webhook Listener for Local Development

This script creates a simple webhook receiver for testing Stripe events locally.
Use with: stripe listen --forward-to localhost:8001/webhook

Run this in one terminal while your main FastAPI app runs on 8000.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import stripe
import os
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

app = FastAPI()

# Stripe configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY_TEST')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

# Log file for webhook events
LOG_FILE = 'webhook_events.log'

def log_webhook(event_type: str, event_id: str, data: dict):
    """Log webhook events to file and console"""
    timestamp = datetime.now().isoformat()
    log_entry = {
        'timestamp': timestamp,
        'event_type': event_type,
        'event_id': event_id,
        'data': data
    }
    
    print(f"\n{'='*60}")
    print(f"✅ WEBHOOK RECEIVED: {event_type}")
    print(f"Event ID: {event_id}")
    print(f"Timestamp: {timestamp}")
    print(f"Data: {json.dumps(data, indent=2)}")
    print(f"{'='*60}\n")
    
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


@app.post("/webhook")
async def webhook(request: Request):
    """Handle incoming Stripe webhooks"""
    
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        print(f"Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        print(f"Invalid signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle specific event types
    event_type = event['type']
    event_id = event['id']
    
    # Log all events
    log_webhook(event_type, event_id, event.get('data', {}))
    
    # Handle payment intent events
    if event_type == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        print(f"✨ Payment succeeded: {payment_intent['id']}")
        # TODO: Update database subscription status
    
    elif event_type == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        print(f"❌ Payment failed: {payment_intent['id']}")
        # TODO: Handle failed payment
    
    # Handle customer subscription events
    elif event_type == 'customer.subscription.created':
        subscription = event['data']['object']
        print(f"📝 Subscription created: {subscription['id']}")
        # TODO: Store subscription in database
    
    elif event_type == 'customer.subscription.updated':
        subscription = event['data']['object']
        print(f"📝 Subscription updated: {subscription['id']}")
        # TODO: Update subscription in database
    
    elif event_type == 'customer.subscription.deleted':
        subscription = event['data']['object']
        print(f"🗑️ Subscription deleted: {subscription['id']}")
        # TODO: Mark subscription as cancelled
    
    elif event_type == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        print(f"💳 Invoice paid: {invoice['id']}")
        # TODO: Update invoice status
    
    elif event_type == 'invoice.payment_failed':
        invoice = event['data']['object']
        print(f"💳 Invoice payment failed: {invoice['id']}")
        # TODO: Handle failed invoice payment
    
    return JSONResponse({'success': True})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({'status': 'ok'})


@app.get("/webhook-events")
async def get_events():
    """Retrieve logged webhook events"""
    events = []
    try:
        with open(LOG_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))
    except FileNotFoundError:
        pass
    
    return JSONResponse({'events': events, 'total': len(events)})


if __name__ == "__main__":
    import uvicorn
    print("🚀 Stripe Webhook Listener starting on http://localhost:8001")
    print("Run in another terminal: stripe listen --forward-to localhost:8001/webhook")
    uvicorn.run(app, host="0.0.0.0", port=8001)