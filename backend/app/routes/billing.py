"""
Two-step payment confirmation flow:
  Step 1 — POST /api/billing/setup-intent    collect card via SetupIntent (no charge)
  Step 2 — POST /api/billing/confirm         attach PM, create monthly sub, return client_secret
  Confirm— handled client-side via stripe.confirmCardPayment(client_secret)
  Webhook — invoice.payment_succeeded → generate token → send activation email
  Redeem — GET /api/billing/activate/{token} → activate workspace, return agent list
  Refund — POST /api/billing/refund-request  full refund within 72h if no tasks executed
"""
import json
import logging
import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, field_validator
from sqlalchemy import text
from sqlalchemy.orm import Session

import stripe

from app.auth import verify_token
from app.config import get_config
from app.database import SessionLocal
from app.limiter import limiter
from app.models import Organization, User, Workspace
from app.models.activation_token import ActivationToken
from app.models.agent_system import AgentJob
from app.services.email_service import send_activation_link
from app.services.stripe_service import StripeService

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/billing", tags=["billing"])
security = HTTPBearer(auto_error=False)

FRONTEND_URL = get_config("FRONTEND_URL", "https://vantro.ai")

# Plan → Stripe price IDs (mirrors stripe.py)
PLANS: dict[str, str] = {
    "starter":  "price_1TYETlRzylDxVczCrgdrs3bd",
    "growth":   "price_1TYEUWRzylDxVczCLB18Hn4v",
    "business": "price_1TYEVoRzylDxVczC6feMM4AE",
}

PLAN_CREDITS: dict[str, int] = {
    "starter": 50,
    "growth": 150,
    "business": 300,
}

# Video credit rules: 1 credit per 15 seconds (minimum 1 credit)
VIDEO_CREDIT_INTERVAL_SECONDS = 15

# Max video duration per plan in seconds (0 = unlimited)
PLAN_MAX_VIDEO_SECONDS: dict[str, int] = {
    "starter": 30,
    "growth": 90,
    "business": 90,
}

# Max video resolution per plan
PLAN_MAX_RESOLUTION: dict[str, str] = {
    "starter": "720p",
    "growth": "1080p",
    "business": "4K",
}

PLAN_PRICES_CENTS: dict[str, int] = {
    "starter": 9900,
    "growth": 27900,
    "business": 39900,
}

# Max agent slots per plan
PLAN_SLOTS: dict[str, int] = {
    "starter": 2,
    "growth": 5,
    "business": 11,
}

# Default agent set per plan (used as fallback when client doesn't select)
PLAN_AGENTS: dict[str, list[str]] = {
    "starter": [
        "intake_trial_agent", "content_strategy_agent",
    ],
    "growth": [
        "intake_trial_agent", "content_strategy_agent", "social_media_agent",
        "email_marketing_agent", "seo_agent",
    ],
    "business": [
        "intake_trial_agent", "content_strategy_agent", "social_media_agent",
        "email_marketing_agent", "seo_agent", "brand_voice_agent",
        "paid_ads_agent", "conversion_optimizer_agent", "customer_success_agent",
        "competitor_analyst_agent", "research_analytics_agent",
    ],
}

AGENT_DISPLAY_NAMES: dict[str, str] = {
    "intake_trial_agent": "Intake & Onboarding",
    "content_strategy_agent": "Content Strategy",
    "social_media_agent": "Social Media",
    "email_marketing_agent": "Email Marketing",
    "seo_agent": "SEO Optimizer",
    "brand_voice_agent": "Brand Voice",
    "paid_ads_agent": "Paid Advertising",
    "conversion_optimizer_agent": "Conversion Optimizer",
    "customer_success_agent": "Customer Success",
    "competitor_analyst_agent": "Competitor Analysis",
    "research_analytics_agent": "Research & Analytics",
    "product_launch_agent": "Product Launch",
    "influencer_outreach_agent": "Influencer Outreach",
    "pr_media_agent": "PR & Media",
    "affiliate_partnership_agent": "Affiliate & Partnerships",
    "video_script_agent": "Video Script",
    "copywriting_agent": "Copywriting",
    "lead_generation_agent": "Lead Generation",
    "retention_agent": "Retention",
    "growth_hacking_agent": "Growth Hacking",
    "market_expansion_agent": "Market Expansion",
    "campaign_orchestrator_agent": "Campaign Orchestrator",
}


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


def _get_workspace(user: User, db: Session) -> Workspace:
    org = db.query(Organization).filter(Organization.owner_id == user.id).first()
    if not org:
        raise HTTPException(status_code=400, detail="No organization found")
    ws = db.query(Workspace).filter(Workspace.organization_id == org.id).first()
    if not ws:
        raise HTTPException(status_code=400, detail="No workspace found")
    return ws


def _validate_agent_selection(agent_ids: list[str], plan: str) -> list[str]:
    """Validate agent selection against plan slot limit and known agent IDs. Returns cleaned list."""
    unknown = [aid for aid in agent_ids if aid not in AGENT_DISPLAY_NAMES]
    if unknown:
        raise HTTPException(status_code=400, detail=f"Unknown agent IDs: {unknown}")
    max_slots = PLAN_SLOTS.get(plan, 0)
    if len(agent_ids) > max_slots:
        raise HTTPException(
            status_code=400,
            detail=f"{plan.capitalize()} plan allows {max_slots} agents; {len(agent_ids)} selected",
        )
    if len(agent_ids) == 0:
        raise HTTPException(status_code=400, detail="Select at least one agent")
    # Deduplicate preserving order
    seen: set[str] = set()
    return [a for a in agent_ids if not (a in seen or seen.add(a))]  # type: ignore[func-returns-value]


def _issue_activation_token(
    workspace_id: str, plan: str, subscription_id: str, db: Session,
    agent_ids: list[str] | None = None,
) -> str:
    if agent_ids is None:
        agent_ids = PLAN_AGENTS.get(plan, [])
    raw_token, token_hash = ActivationToken.generate()
    record = ActivationToken(
        workspace_id=workspace_id,
        token_hash=token_hash,
        plan=plan,
        agent_ids=json.dumps(agent_ids),
        stripe_subscription_id=subscription_id,
        expires_at=ActivationToken.default_expiry(),
    )
    db.add(record)
    db.commit()
    return raw_token


# ─── Step 1: Create SetupIntent ────────────────────────────────────────────────

class SetupIntentRequest(BaseModel):
    plan: str
    agent_ids: list[str] = []


@router.post("/setup-intent")
@limiter.limit("20/minute")
async def create_setup_intent(
    request: Request,
    body: SetupIntentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Step 1 — create a SetupIntent so the client can collect card details without charging."""
    if body.plan not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")
    # Validate + lock agent selection
    selected = _validate_agent_selection(body.agent_ids, body.plan) if body.agent_ids else PLAN_AGENTS.get(body.plan, [])
    user = _get_user(credentials, db)
    try:
        customer_id = StripeService.get_or_create_customer(
            user.email, user.name or user.email, user.stripe_customer_id
        )
        if not user.stripe_customer_id:
            user.stripe_customer_id = customer_id
            db.commit()
        client_secret = StripeService.create_setup_intent(customer_id)
        return {
            "client_secret": client_secret,
            "plan": body.plan,
            "amount_cents": PLAN_PRICES_CENTS[body.plan],
            "credits": PLAN_CREDITS[body.plan],
            "agents": [
                {"id": aid, "name": AGENT_DISPLAY_NAMES.get(aid, aid)}
                for aid in selected
            ],
            "selected_agent_ids": selected,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("setup-intent error for user %s: %s", user.id, exc)
        raise HTTPException(status_code=400, detail="Unable to initialize payment")


# ─── Step 2: Confirm & Subscribe ───────────────────────────────────────────────

class ConfirmRequest(BaseModel):
    payment_method_id: str
    plan: str
    agent_ids: list[str] = []


@router.post("/confirm")
@limiter.limit("10/minute")
async def confirm_subscription(
    request: Request,
    body: ConfirmRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Step 2 — attach payment method, create monthly subscription.
    Returns {client_secret} which the frontend must confirm via stripe.confirmCardPayment().
    The activation email is sent after the webhook confirms payment_succeeded.
    """
    if body.plan not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")
    if not body.payment_method_id.startswith("pm_"):
        raise HTTPException(status_code=400, detail="Invalid payment method")
    # Validate + lock agent selection — cannot be changed after this point
    selected = _validate_agent_selection(body.agent_ids, body.plan) if body.agent_ids else PLAN_AGENTS.get(body.plan, [])
    user = _get_user(credentials, db)
    if not user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No billing account found — complete step 1 first")
    try:
        result = StripeService.attach_pm_and_subscribe(
            customer_id=user.stripe_customer_id,
            pm_id=body.payment_method_id,
            price_id=PLANS[body.plan],
        )
        # Lock agent selection, store subscription ID + period end, mark pending payment
        db.execute(
            text(
                "UPDATE users SET subscription_status='pending_first_payment',"
                " locked_agent_ids=:agent_ids,"
                " stripe_subscription_id=:sub_id,"
                " subscription_period_end=:period_end"
                " WHERE id=:uid"
            ),
            {
                "uid": user.id,
                "agent_ids": json.dumps(selected),
                "sub_id": result["subscription_id"],
                "period_end": result.get("period_end"),
            },
        )
        db.commit()
        return {
            "subscription_id": result["subscription_id"],
            "client_secret": result["client_secret"],
            "status": result["status"],
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("confirm-subscription error for user %s: %s", user.id, exc)
        raise HTTPException(status_code=400, detail="Subscription creation failed")


# ─── Webhook handler (wired via stripe.py webhook endpoint) ────────────────────
# Called by the existing stripe webhook route after invoice.payment_succeeded
# for the FIRST payment (subscription_status='pending_first_payment').

def handle_first_payment_succeeded(user: User, plan: str, subscription_id: str, db: Session) -> None:
    """Send activation email with one-time link. Called from stripe webhook."""
    try:
        ws = _get_workspace_for_user(user, db)
        if ws is None:
            logger.warning("No workspace for user %s — skipping activation email", user.id)
            return
        # Use client's locked selection; fall back to plan defaults if missing
        locked_raw = db.execute(
            text("SELECT locked_agent_ids FROM users WHERE id=:uid"), {"uid": user.id}
        ).scalar()
        locked_ids: list[str] = json.loads(locked_raw) if locked_raw else PLAN_AGENTS.get(plan, [])
        raw_token = _issue_activation_token(ws.id, plan, subscription_id, db, agent_ids=locked_ids)
        activation_url = f"{FRONTEND_URL}/activate/{raw_token}"
        agent_names = [AGENT_DISPLAY_NAMES.get(aid, aid) for aid in locked_ids]
        send_activation_link(
            to_email=user.email,
            name=user.name or "there",
            activation_url=activation_url,
            plan=plan,
            agent_names=agent_names,
        )
        logger.info(
            "Activation link sent to %s (plan=%s, workspace=%s)", user.email, plan, ws.id
        )
    except Exception as exc:
        logger.error("handle_first_payment_succeeded error for user %s: %s", user.id, exc)


def _get_workspace_for_user(user: User, db: Session) -> Workspace | None:
    org = db.query(Organization).filter(Organization.owner_id == user.id).first()
    if not org:
        return None
    return db.query(Workspace).filter(Workspace.organization_id == org.id).first()


# ─── Activation redemption ─────────────────────────────────────────────────────

@router.get("/activate/{token}")
@limiter.limit("5/minute")
async def activate_workspace(
    request: Request,
    token: str,
    db: Session = Depends(get_db),
):
    """
    Redeem one-time activation link.
    Marks workspace as active, burns token, returns plan + agent list.
    Public endpoint — no auth required (the token IS the proof of payment).
    """
    if not token or len(token) < 20:
        raise HTTPException(status_code=400, detail="Invalid activation link")

    token_hash = ActivationToken.hash(token)
    record = (
        db.query(ActivationToken)
        .filter(ActivationToken.token_hash == token_hash)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Activation link not found or already used")
    if record.used_at:
        raise HTTPException(status_code=410, detail="This activation link has already been used")
    if datetime.utcnow() > record.expires_at:
        raise HTTPException(status_code=410, detail="Activation link has expired")

    # Burn the token
    record.used_at = datetime.utcnow()

    # Activate workspace
    ws = db.query(Workspace).filter(Workspace.id == record.workspace_id).first()
    if ws:
        ws.is_active = True  # type: ignore[attr-defined]

    db.commit()

    agent_ids = json.loads(record.agent_ids or "[]")
    agents = [{"id": aid, "name": AGENT_DISPLAY_NAMES.get(aid, aid)} for aid in agent_ids]

    return {
        "activated": True,
        "plan": record.plan,
        "agents": agents,
        "message": f"Your {record.plan.capitalize()} workspace is now active",
    }


# ─── Refund Request ────────────────────────────────────────────────────────────

_REFUND_WINDOW_HOURS = 72
_EXECUTED_STATUSES = ("pending", "failed")  # statuses that do NOT count as executed


@router.post("/refund-request")
@limiter.limit("5/minute")
async def request_refund(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Full refund if:
      - Zero agent jobs with an executed status (anything other than 'pending' / 'failed')
      - Account created within the last 72 hours
    On approval: issues Stripe refund on latest invoice, cancels subscription, updates DB.
    """
    user = _get_user(credentials, db)
    ws = _get_workspace_for_user(user, db)
    if not ws:
        raise HTTPException(status_code=400, detail="No workspace found")

    # 1. Check for executed jobs (workspace-scoped)
    executed_count = (
        db.query(AgentJob)
        .filter(
            AgentJob.workspace_id == ws.id,
            AgentJob.status.notin_(_EXECUTED_STATUSES),
        )
        .count()
    )
    if executed_count > 0:
        raise HTTPException(
            status_code=403,
            detail="Refund not available: agent tasks have been executed.",
        )

    # 2. Check 72-hour refund window (use workspace.created_at; fall back to user.created_at)
    created_at = ws.created_at or user.created_at
    if created_at is None:
        raise HTTPException(status_code=400, detail="Account creation date unavailable")
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    now_utc = datetime.now(timezone.utc)
    if now_utc - created_at > timedelta(hours=_REFUND_WINDOW_HOURS):
        raise HTTPException(
            status_code=403,
            detail="Refund window has closed (72 hours from account creation).",
        )

    # 3. Resolve Stripe customer + subscription
    customer_id = user.stripe_customer_id
    subscription_id = user.stripe_subscription_id
    if not customer_id:
        raise HTTPException(status_code=400, detail="No billing account found")

    try:
        # Fetch the latest invoice for this customer to get the payment_intent
        invoices = stripe.Invoice.list(customer=customer_id, limit=1)
        if not invoices.data:
            raise HTTPException(status_code=400, detail="No invoice found for your account")

        latest_invoice = invoices.data[0]
        payment_intent_id = latest_invoice.get("payment_intent")
        if not payment_intent_id:
            raise HTTPException(status_code=400, detail="No charge found to refund")

        # Issue full refund
        stripe.Refund.create(
            payment_intent=payment_intent_id,
            reason="requested_by_customer",
        )

        # Cancel Stripe subscription
        if subscription_id:
            try:
                stripe.Subscription.delete(subscription_id)
            except stripe.error.StripeError:
                logger.warning(
                    "Could not cancel Stripe subscription %s during refund for user %s",
                    subscription_id,
                    user.id,
                )

        # Mark subscription as cancelled in DB
        db.execute(
            text(
                "UPDATE users SET subscription_status='cancelled'"
                " WHERE id=:uid"
            ),
            {"uid": user.id},
        )
        db.commit()

        logger.info(
            "Refund processed for user %s (workspace=%s, invoice=%s)",
            user.id,
            ws.id,
            latest_invoice.id,
        )
        return {"detail": "Refund processed. Your subscription has been cancelled."}

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Refund error for user %s: %s", user.id, exc)
        raise HTTPException(status_code=500, detail="An error occurred while processing your refund. Please contact support.")
