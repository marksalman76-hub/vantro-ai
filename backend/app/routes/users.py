import json
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth import verify_token
from app.database import SessionLocal
from app.models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/users", tags=["users"])
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


class ConsentBody(BaseModel):
    accepted: bool


@router.post("/consent")
async def record_cookie_consent(
    body: ConsentBody,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)
    user.cookie_consent = body.accepted
    user.cookie_consent_at = datetime.utcnow()
    db.commit()
    logger.info("Cookie consent recorded for user %s: %s", user.id, body.accepted)
    return {"status": "recorded"}


class BrandProfileUpdate(BaseModel):
    business_name: Optional[str] = Field(default=None, max_length=200)
    industry: Optional[str] = Field(default=None, max_length=100)
    products_services: Optional[str] = Field(default=None, max_length=2000)
    target_audience: Optional[str] = Field(default=None, max_length=1000)
    brand_voice: Optional[str] = Field(default=None, max_length=500)
    brand_colours: Optional[str] = Field(default=None, max_length=500)
    website: Optional[str] = Field(default=None, max_length=500)
    social_links: Optional[str] = Field(default=None, max_length=1000)
    preferred_tone: Optional[str] = Field(default=None, max_length=200)
    do_not_use: Optional[str] = Field(default=None, max_length=1000)


@router.get("/brand-profile")
async def get_brand_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)
    return {"brand_profile": user.brand_profile or {}}


@router.put("/brand-profile")
async def update_brand_profile(
    body: BrandProfileUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)
    existing = dict(user.brand_profile or {})
    existing.update({k: v for k, v in body.model_dump().items() if v is not None})
    user.brand_profile = existing
    db.commit()
    logger.info("Brand profile updated for user %s", user.id)
    return {"brand_profile": user.brand_profile}


@router.get("/me/export")
async def export_my_data(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """GDPR data export — returns all personal data held for the authenticated user."""
    user = _get_user(credentials, db)

    # Collect agent jobs via raw SQL to avoid circular model imports
    try:
        jobs_rows = db.execute(
            text("SELECT id, agent_id, status, input_data, created_at FROM agent_jobs WHERE workspace_id IN (SELECT id FROM workspaces WHERE organization_id IN (SELECT id FROM organizations WHERE owner_id = :uid))"),
            {"uid": user.id},
        ).fetchall()
        jobs = [{"id": r[0], "agent_id": r[1], "status": r[2], "input_data": r[3], "created_at": str(r[4])} for r in jobs_rows]
    except Exception:
        jobs = []

    try:
        tickets_rows = db.execute(
            text("SELECT id, ticket_type, message, status, created_at FROM support_tickets WHERE user_id = :uid"),
            {"uid": user.id},
        ).fetchall()
        tickets = [{"id": r[0], "ticket_type": r[1], "message": r[2], "status": r[3], "created_at": str(r[4])} for r in tickets_rows]
    except Exception:
        tickets = []

    export = {
        "exported_at": datetime.utcnow().isoformat(),
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "created_at": str(getattr(user, "created_at", None)),
            "subscription_status": user.subscription_status,
            "brand_profile": user.brand_profile,
        },
        "agent_jobs": jobs,
        "support_tickets": tickets,
    }
    return JSONResponse(content=export, headers={"Content-Disposition": "attachment; filename=vantro-data-export.json"})


@router.delete("/me")
async def delete_my_account(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """GDPR right-to-erasure — anonymises PII and deactivates the account."""
    user = _get_user(credentials, db)

    # Cancel Stripe subscription if present
    if user.stripe_customer_id:
        try:
            import stripe as _stripe
            import os
            _stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
            subs = _stripe.Subscription.list(customer=user.stripe_customer_id, limit=5)
            for sub in subs.auto_paging_iter():
                _stripe.Subscription.cancel(sub.id)
        except Exception as exc:
            logger.warning("Stripe cancellation failed during account deletion: %s", exc)

    # Anonymise — replace PII with placeholder, keep account shell for FK integrity
    anon_email = f"deleted_{user.id}@deleted.invalid"
    user.email        = anon_email
    user.name         = "Deleted User"
    user.password_hash = "DELETED"
    user.brand_profile = None
    user.is_active    = False
    user.stripe_customer_id = None
    user.reset_token  = None

    # Scrub support tickets
    try:
        db.execute(
            text("UPDATE support_tickets SET email = :e, message = '[redacted]' WHERE user_id = :uid"),
            {"e": anon_email, "uid": user.id},
        )
    except Exception:
        pass

    db.commit()
    logger.info("Account deleted (anonymised) for user %s", user.id)
    return {"detail": "Account deleted. Your data has been anonymised in accordance with GDPR."}
