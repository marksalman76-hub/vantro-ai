import os
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth import verify_token
from app.config import get_config
from app.database import SessionLocal
from app.limiter import limiter
from app.models import User, Organization
from app.models.workspace import Workspace, CreditsAccount
from app.services.stripe_service import StripeService
from app.services.email_service import send_payment_failed
from app.routes.billing import handle_first_payment_succeeded

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

FRONTEND_URL = get_config("FRONTEND_URL", "https://vantro.ai")


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


# Top-up packs: credits → unit price in cents
TOPUP_PACKS: dict[int, int] = {10: 1500, 25: 3500, 50: 6500}


class CreateCheckoutRequest(BaseModel):
    plan: str  # "starter" | "growth" | "business"


class CreateTopupRequest(BaseModel):
    credits: int  # 10 | 25 | 50


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


@router.post("/create-topup-checkout")
async def create_topup_checkout(
    request: CreateTopupRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)
    price_cents = TOPUP_PACKS.get(request.credits)
    if not price_cents:
        raise HTTPException(status_code=400, detail=f"Invalid top-up pack: {request.credits} credits")
    try:
        customer_id = StripeService.create_customer(user.email, user.name or user.email)
        session = StripeService.create_topup_checkout_session(
            customer_id=customer_id,
            credits=request.credits,
            price_cents=price_cents,
            success_url=f"{FRONTEND_URL}/dashboard?topup=success&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{FRONTEND_URL}/pricing",
            client_reference_id=user.id,
        )
        return {"checkout_url": session["url"], "session_id": session["id"]}
    except Exception as e:
        logger.error("Top-up checkout error: %s", e)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/customer-portal")
async def create_customer_portal(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)
    if not user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No billing account found. Subscribe to a plan first.")
    try:
        result = StripeService.create_customer_portal_session(
            customer_id=user.stripe_customer_id,
            return_url=f"{FRONTEND_URL}/dashboard",
        )
        return result
    except Exception as e:
        logger.error("Customer portal error: %s", e)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/config")
async def get_stripe_config():
    pub_key = get_config("STRIPE_PUBLISHABLE_KEY", "")
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


def _add_topup_credits(user: User, credits: int, db: Session) -> None:
    """Add purchased top-up credits on top of existing balance (does not reset used_credits)."""
    from datetime import datetime
    import uuid

    org = db.query(Organization).filter(Organization.owner_id == user.id).first()
    if not org:
        logger.warning("No org found for user %s — skipping topup", user.id)
        return
    workspace = db.query(Workspace).filter(Workspace.organization_id == org.id).first()
    if not workspace:
        logger.warning("No workspace found for user %s — skipping topup", user.id)
        return
    acct = db.query(CreditsAccount).filter(CreditsAccount.workspace_id == workspace.id).first()
    if acct:
        acct.total_credits += credits
    else:
        acct = CreditsAccount(
            id=str(uuid.uuid4()),
            workspace_id=workspace.id,
            total_credits=credits,
            used_credits=0,
            created_at=datetime.utcnow(),
        )
        db.add(acct)
    logger.info("Added %d top-up credits for user %s (new total=%s)", credits, user.id,
                acct.total_credits if acct else credits)


@router.post("/webhook")
@limiter.limit("300/minute")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    webhook_secret = get_config("STRIPE_WEBHOOK_SECRET", "")

    if not webhook_secret:
        raise HTTPException(status_code=503, detail="Webhook secret not configured")

    event = StripeService.verify_webhook(payload, sig_header, webhook_secret)
    if not event:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_id = event["id"]
    event_type = event["type"]
    logger.info("Stripe event: %s id=%s", event_type, event_id)

    # Idempotency guard — return 200 immediately on replay to prevent double-processing
    already = db.execute(
        text("SELECT 1 FROM stripe_webhook_events WHERE id = :eid"),
        {"eid": event_id},
    ).first()
    if already:
        logger.info("Skipping duplicate Stripe event %s", event_id)
        return {"status": "already_processed"}

    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("client_reference_id")
        metadata = session.get("metadata") or {}
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                if metadata.get("type") == "topup":
                    extra_credits = int(metadata.get("credits", 0))
                    if extra_credits > 0:
                        _add_topup_credits(user, extra_credits, db)
                        logger.info("Top-up %d credits for user %s", extra_credits, user_id)
                else:
                    plan = metadata.get("plan", "")
                    user.subscription_status = "active"
                    user.stripe_customer_id = session.get("customer")
                    _assign_credits(user, plan, db)
                    logger.info("Activated subscription (plan=%s) for user %s", plan, user_id)

    elif event_type == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        customer_id = invoice.get("customer")
        subscription_id = invoice.get("subscription", "")
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            lines = invoice.get("lines", {}).get("data", [])
            price_id = lines[0].get("price", {}).get("id") if lines else None
            plan = PRICE_TO_PLAN.get(price_id, "")
            # Track subscription ID and period end for pre-billing reminder job
            if subscription_id and not user.stripe_subscription_id:
                user.stripe_subscription_id = subscription_id
            period_end_ts = lines[0].get("period", {}).get("end") if lines else None
            if period_end_ts:
                user.subscription_period_end = datetime.utcfromtimestamp(period_end_ts)
            if plan:
                _assign_credits(user, plan, db)
                logger.info("Assigned %s credits to user %s (invoice %s)", plan, user.id, invoice.get("id"))
                # First payment — activate subscription and send one-time link
                if user.subscription_status in ("pending_first_payment", None, ""):
                    user.subscription_status = "active"
                    handle_first_payment_succeeded(user, plan, subscription_id, db)
                else:
                    user.subscription_status = "active"

    elif event_type == "payment_intent.payment_failed":
        pi = event["data"]["object"]
        customer_id = pi.get("customer")
        if customer_id:
            user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
            if user:
                user.subscription_status = "past_due"
                error_msg = pi.get("last_payment_error", {}).get("message", "")
                logger.warning(
                    "Payment failed for user %s (customer %s): %s",
                    user.id, customer_id, error_msg or "unknown",
                )
                try:
                    send_payment_failed(user.email, user.name or "there", error_msg)
                except Exception:
                    logger.exception("Failed to send payment failed email to %s", user.email)

    elif event_type == "customer.subscription.updated":
        sub = event["data"]["object"]
        customer_id = sub.get("customer")
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            user.subscription_status = sub.get("status")

    elif event_type == "customer.subscription.deleted":
        sub = event["data"]["object"]
        customer_id = sub.get("customer")
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            user.subscription_status = "canceled"

    # Mark event as processed before committing — atomic with any model changes above
    db.execute(
        text("INSERT INTO stripe_webhook_events (id, event_type, processed_at) VALUES (:id, :type, :ts)"),
        {"id": event_id, "type": event_type, "ts": datetime.utcnow()},
    )
    db.commit()
    return {"status": "received"}
