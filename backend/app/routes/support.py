import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth import verify_token
from app.database import SessionLocal
from app.models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/support", tags=["support"])
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


VALID_TICKET_STATUSES = {"open", "in_progress", "resolved", "closed"}

class CreateTicketRequest(BaseModel):
    ticket_type: str = Field(..., max_length=50)
    subject: str = Field(..., max_length=200)
    detail: str = Field(..., max_length=5000)
    job_ref: str = Field(default="", max_length=36)


@router.post("/tickets")
async def create_ticket(
    body: CreateTicketRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)
    ticket_id = str(uuid.uuid4())
    message = f"Subject: {body.subject}\n\nDetails: {body.detail}"
    if body.job_ref:
        message += f"\n\nJob reference: {body.job_ref}"

    db.execute(
        text("""
            INSERT INTO support_tickets (id, user_id, email, ticket_type, message, status, created_at)
            VALUES (:id, :user_id, :email, :ticket_type, :message, 'open', :created_at)
        """),
        {
            "id": ticket_id,
            "user_id": user.id,
            "email": user.email,
            "ticket_type": body.ticket_type,
            "message": message,
            "created_at": datetime.utcnow(),
        },
    )
    db.commit()
    logger.info("Support ticket %s created for user %s (type=%s)", ticket_id, user.id, body.ticket_type)
    return {"ticket_id": ticket_id, "status": "open"}


@router.get("/tickets")
async def list_tickets(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)
    rows = db.execute(
        text("SELECT * FROM support_tickets WHERE user_id = :uid ORDER BY created_at DESC LIMIT 50"),
        {"uid": user.id},
    ).fetchall()
    return {"tickets": [dict(r._mapping) for r in rows]}


@router.get("/tickets/all")
async def admin_list_all_tickets(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Admin only — list all support tickets."""
    import os
    user = _get_user(credentials, db)
    admin_email = os.getenv("ADMIN_EMAIL", "")
    if not admin_email or user.email.lower() != admin_email.lower():
        raise HTTPException(status_code=403, detail="Admin access required")
    rows = db.execute(
        text("SELECT * FROM support_tickets ORDER BY created_at DESC LIMIT 200")
    ).fetchall()
    return {"tickets": [dict(r._mapping) for r in rows]}


@router.patch("/tickets/{ticket_id}")
async def update_ticket_status(
    ticket_id: str,
    body: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Admin only — update ticket status."""
    import os
    user = _get_user(credentials, db)
    admin_email = os.getenv("ADMIN_EMAIL", "")
    if not admin_email or user.email.lower() != admin_email.lower():
        raise HTTPException(status_code=403, detail="Admin access required")
    new_status = body.get("status", "resolved")
    if new_status not in VALID_TICKET_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(sorted(VALID_TICKET_STATUSES))}")
    db.execute(
        text("UPDATE support_tickets SET status = :status, updated_at = :ts WHERE id = :id"),
        {"status": new_status, "ts": datetime.utcnow(), "id": ticket_id},
    )
    db.commit()
    return {"ticket_id": ticket_id, "status": new_status}
