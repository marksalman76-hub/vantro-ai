from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import stripe
import os
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

app = FastAPI()

stripe.api_key = os.getenv('STRIPE_SECRET_KEY_TEST')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

LOG_FILE = 'webhook_events.log'

def log_webhook(event_type: str, event_id: str, data: dict):
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
    print(f"{'='*60}\n")
    
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    event_type = event['type']
    event_id = event['id']
    
    log_webhook(event_type, event_id, event.get('data', {}))
    
    if event_type == 'payment_intent.succeeded':
        print(f"✨ Payment succeeded: {event['data']['object']['id']}")
    elif event_type == 'payment_intent.payment_failed':
        print(f"❌ Payment failed: {event['data']['object']['id']}")
    elif event_type == 'customer.subscription.created':
        print(f"📝 Subscription created: {event['data']['object']['id']}")
    elif event_type == 'customer.subscription.updated':
        print(f"📝 Subscription updated: {event['data']['object']['id']}")
    elif event_type == 'customer.subscription.deleted':
        print(f"🗑️ Subscription deleted: {event['data']['object']['id']}")
    elif event_type == 'invoice.payment_succeeded':
        print(f"💳 Invoice paid: {event['data']['object']['id']}")
    elif event_type == 'invoice.payment_failed':
        print(f"💳 Invoice payment failed: {event['data']['object']['id']}")
    
    return JSONResponse({'success': True})


@app.get("/health")
async def health_check():
    return JSONResponse({'status': 'ok'})


@app.get("/webhook-events")
async def get_events():
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
    uvicorn.run(app, host="0.0.0.0", port=8001)