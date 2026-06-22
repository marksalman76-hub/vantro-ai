import os
import logging
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import verify_token
from app.database import SessionLocal
from app.models import User, Organization
from app.models.workspace import Workspace, CreditsAccount
from app.services.stripe_service import StripeService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/stripe", tags=["stripe"])
security = HTTPBearer(auto_error=False)

PLANS = {
    "starter":  "price_1TYETlRzylDxVczCrgdrs3bd",
    "growth":   "price_1TYEUWRzylDxVczCLB18Hn4v",
    "business": "price_1TYEVoRzylDxVczC6feMM4AE",
}

# Credits per plan — calculated for 40% margin at $0.75/video generation cost, $15/mo fixed infra
PLAN_CREDITS = {
    "starter":  60,   # $99/mo  → budget $44.40 / $0.75 = 59.2 → 60
    "growth":   200,  # $279/mo → budget $152.40 / $0.75 = 203.2 → 200
    "business": 300,  # $399/mo → budget $224.40 / $0.75 = 299.2 → 300
}

# Map Stripe price_id → plan name (for renewal events that don't carry metadata)
PRICE_TO_PLAN = {v: k for k, v in PLANS.items()}

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://www.vantro.ai")


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


class CreateCheckoutRequest(BaseModel):
    plan: str  # "starter" | "growth" | "business"


class CreatePaymentRequest(BaseModel):
    amount_cents: int
    description: str = ""


class CreateSubscriptionRequest(BaseModel):
    price_id: str


@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CreateCheckoutRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)
    price_id = PLANS.get(request.plan)
    if not price_id:
        raise HTTPException(status_code=400, detail=f"Unknown plan: {request.plan}")
    try:
        customer_id = StripeService.create_customer(user.email, user.name or user.email)
        session = StripeService.create_checkout_session(
            customer_id=customer_id,
            price_id=price_id,
            success_url=f"{FRONTEND_URL}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{FRONTEND_URL}/pricing",
            client_reference_id=user.id,
            plan=request.plan,
        )
        return {"checkout_url": session["url"], "session_id": session["id"]}
    except Exception as e:
        logger.error("Checkout session error: %s", e)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/plans")
async def get_plans():
    return {
        "plans": [
            {"id": "starter",  "name": "Starter",  "price_id": PLANS["starter"],  "amount": 9900,  "currency": "usd"},
            {"id": "growth",   "name": "Growth",   "price_id": PLANS["growth"],   "amount": 27900, "currency": "usd"},
            {"id": "business", "name": "Business", "price_id": PLANS["business"], "amount": 39900, "currency": "usd"},
        ]
    }


@router.post("/create-payment-intent")
async def create_payment_intent(
    request: CreatePaymentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)
    try:
        customer_id = StripeService.create_customer(user.email, user.name or user.email)
        result = StripeService.create_payment_intent(
            request.amount_cents,
            customer_id,
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
        customer_id = StripeService.create_customer(user.email, user.name or user.email)
        result = StripeService.create_subscription(customer_id, request.price_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/config")
async def get_stripe_config():
    pub_key = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    if not pub_key:
        raise HTTPException(status_code=503, detail="Stripe not configured")
    return {"publishable_key": pub_key}


def _assign_credits(user: User, plan: str, db: Session) -> None:
    """Set the monthly credit allocation for a user's workspace. Resets used_credits to 0."""
    credits_to_assign = PLAN_CREDITS.get(plan, 0)
    if credits_to_assign == 0:
        return

    org = db.query(Organization).filter(Organization.owner_id == user.id).first()
    if not org:
        logger.warning("No org found for user %s — skipping credit assignment", user.id)
        return

    workspace = db.query(Workspace).filter(Workspace.organization_id == org.id).first()
    if not workspace:
        logger.warning("No workspace found for user %s — skipping credit assignment", user.id)
        return

    acct = db.query(CreditsAccount).filter(CreditsAccount.workspace_id == workspace.id).first()
    if acct:
        acct.total_credits = credits_to_assign
        acct.used_credits = 0
    else:
        from datetime import datetime
        import uuid
        acct = CreditsAccount(
            id=str(uuid.uuid4()),
            workspace_id=workspace.id,
            total_credits=credits_to_assign,
            used_credits=0,
            created_at=datetime.utcnow(),
        )
        db.add(acct)

    logger.info("Assigned %d credits (plan=%s) to user %s", credits_to_assign, plan, user.id)


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    if not webhook_secret:
        raise HTTPException(status_code=503, detail="Webhook secret not configured")

    event = StripeService.verify_webhook(payload, sig_header, webhook_secret)
    if not event:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]
    logger.info("Stripe event: %s", event_type)

    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("client_reference_id")
        plan = (session.get("metadata") or {}).get("plan", "")
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.subscription_status = "active"
                user.stripe_customer_id = session.get("customer")
                _assign_credits(user, plan, db)
                db.commit()
                logger.info("Activated subscription (plan=%s) for user %s", plan, user_id)

    elif event_type == "invoice.payment_succeeded":
        # Monthly renewal — refresh credit allocation
        invoice = event["data"]["object"]
        customer_id = invoice.get("customer")
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user and user.subscription_status == "active":
            # Get plan from the subscription's price ID
            lines = invoice.get("lines", {}).get("data", [])
            price_id = lines[0].get("price", {}).get("id") if lines else None
            plan = PRICE_TO_PLAN.get(price_id, "")
            if plan:
                _assign_credits(user, plan, db)
                db.commit()
                logger.info("Renewed %s credits for user %s (invoice %s)", plan, user.id, invoice.get("id"))

    elif event_type == "customer.subscription.updated":
        sub = event["data"]["object"]
        customer_id = sub.get("customer")
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            user.subscription_status = sub.get("status")
            db.commit()

    elif event_type == "customer.subscription.deleted":
        sub = event["data"]["object"]
        customer_id = sub.get("customer")
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            user.subscription_status = "canceled"
            db.commit()

    return {"status": "received"}
