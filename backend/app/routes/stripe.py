import os
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import verify_token
from app.database import SessionLocal
from app.models import User
from app.services.stripe_service import StripeService

router = APIRouter(prefix="/api/stripe", tags=["stripe"])
security = HTTPBearer(auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_user(credentials: HTTPAuthorizationCredentials, db: Session) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


class CreatePaymentRequest(BaseModel):
    amount_cents: int
    description: str = ""


class CreateSubscriptionRequest(BaseModel):
    price_id: str


@router.post("/create-payment-intent")
async def create_payment_intent(
    request: CreatePaymentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)
    try:
        result = StripeService.create_payment_intent(
            request.amount_cents,
            f"cus_{user.id}",
            request.description,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/create-subscription")
async def create_subscription(
    request: CreateSubscriptionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)
    try:
        # Ensure Stripe customer exists for this user
        customer_id = StripeService.create_customer(user.email, user.name or user.email)
        result = StripeService.create_subscription(customer_id, request.price_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/config")
async def get_stripe_config():
    """Return publishable key for frontend Stripe.js initialization."""
    pub_key = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    if not pub_key:
        raise HTTPException(status_code=503, detail="Stripe not configured")
    return {"publishable_key": pub_key}


@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    if not webhook_secret:
        raise HTTPException(status_code=503, detail="Webhook secret not configured")

    event = StripeService.verify_webhook(payload, sig_header, webhook_secret)
    if not event:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "payment_intent.succeeded":
        pass  # TODO: credit user account
    elif event["type"] == "customer.subscription.updated":
        pass  # TODO: update subscription tier
    elif event["type"] == "customer.subscription.deleted":
        pass  # TODO: downgrade user

    return {"status": "received"}
