from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from backend.app.services.stripe_service import StripeService
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/stripe", tags=["stripe"])

class CreatePaymentRequest(BaseModel):
    amount_cents: int
    description: str = ""

class CreateSubscriptionRequest(BaseModel):
    price_id: str

@router.post("/create-payment-intent")
async def create_payment_intent(request: CreatePaymentRequest, user_id: str):
    try:
        customer_id = f"cus_{user_id}"
        result = StripeService.create_payment_intent(
            request.amount_cents,
            customer_id,
            request.description
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/create-subscription")
async def create_subscription(request: CreateSubscriptionRequest, user_id: str):
    try:
        customer_id = f"cus_{user_id}"
        result = StripeService.create_subscription(customer_id, request.price_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = "whsec_test_placeholder"
    
    event = StripeService.verify_webhook(payload, sig_header, webhook_secret)
    if not event:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    if event.type == "payment_intent.succeeded":
        print(f"Payment succeeded: {event.data.object.id}")
    elif event.type == "customer.subscription.updated":
        print(f"Subscription updated: {event.data.object.id}")
    
    return {"status": "received"}
