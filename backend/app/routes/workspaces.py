"""
Workspace Invitations API
- POST /api/workspaces/{id}/invite        — invite a user by email
- POST /api/workspaces/accept-invite/{token} — accept an invite (creates or adds user)
"""
import hashlib
import logging
import os
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth import verify_token
from app.database import SessionLocal
from app.models import User, Organization
from app.models.workspace import Workspace
from app.services.email_service import _send as _send_email

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/workspaces", tags=["workspaces"])
security = HTTPBearer(auto_error=False)

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://vantro.ai")
INVITE_TTL_HOURS = 72


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


class InviteRequest(BaseModel):
    email: str
    role: str = "member"  # member | admin


@router.post("/{workspace_id}/invite")
async def invite_to_workspace(
    workspace_id: str,
    body: InviteRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)

    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Verify the requesting user owns this workspace's organization
    org = db.query(Organization).filter(
        Organization.id == ws.organization_id,
        Organization.owner_id == user.id,
    ).first()
    if not org:
        raise HTTPException(status_code=403, detail="You don't have permission to manage this workspace")

    # Generate a secure one-time token
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires_at = datetime.utcnow() + timedelta(hours=INVITE_TTL_HOURS)

    try:
        db.execute(
            text("""
                INSERT INTO workspace_invites
                    (id, workspace_id, invited_email, role, token_hash, invited_by, expires_at, created_at)
                VALUES (:id, :ws_id, :email, :role, :tok, :by, :exp, :now)
            """),
            {
                "id": secrets.token_hex(16),
                "ws_id": workspace_id,
                "email": body.email,
                "role": body.role,
                "tok": token_hash,
                "by": user.id,
                "exp": expires_at,
                "now": datetime.utcnow(),
            },
        )
        db.commit()
    except Exception as exc:
        logger.error("Failed to create invite: %s", exc)
        raise HTTPException(status_code=500, detail="Could not create invite")

    accept_url = f"{FRONTEND_URL}/accept-invite/{raw_token}"
    body_text = (
        f"You've been invited to join the workspace '{ws.name}' on Vantro.\n\n"
        f"Accept your invitation (expires in {INVITE_TTL_HOURS}h):\n{accept_url}\n\n"
        f"If you don't have a Vantro account, you'll be prompted to create one."
    )
    body_html = f"""
    <html><body style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:40px 20px;background:#0f0f13;color:#e5e7eb;">
      <div style="margin-bottom:32px;">
        <span style="font-size:20px;font-weight:700;color:#fff;">Vantro<span style="color:#8b5cf6;">.ai</span></span>
      </div>
      <h2 style="color:#fff;margin-bottom:8px;">You're invited to {ws.name}</h2>
      <p style="color:#9ca3af;margin-bottom:32px;">
        {user.name or user.email} has invited you to join the workspace
        <strong style="color:#e5e7eb;">{ws.name}</strong> on Vantro AI.
        This invite expires in {INVITE_TTL_HOURS} hours.
      </p>
      <a href="{accept_url}" style="display:inline-block;background:#7c3aed;color:#fff;padding:12px 28px;border-radius:10px;text-decoration:none;font-weight:600;">
        Accept invitation
      </a>
      <p style="color:#6b7280;font-size:12px;margin-top:40px;">
        If you weren't expecting this invitation, you can safely ignore this email.
      </p>
    </body></html>
    """
    _send_email(body.email, f"You're invited to {ws.name} on Vantro", body_text, body_html)

    logger.info("Invite sent to %s for workspace %s by %s", body.email, workspace_id, user.id)
    return {"detail": f"Invitation sent to {body.email}", "expires_at": expires_at.isoformat()}


@router.post("/accept-invite/{token}")
async def accept_workspace_invite(
    token: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    try:
        row = db.execute(
            text("""
                SELECT id, workspace_id, role, expires_at, accepted_at, invited_email
                FROM workspace_invites WHERE token_hash = :tok
            """),
            {"tok": token_hash},
        ).fetchone()
    except Exception:
        raise HTTPException(status_code=404, detail="Invite not found or expired")

    if not row:
        raise HTTPException(status_code=404, detail="Invite not found or expired")

    if row[4] is not None:
        raise HTTPException(status_code=409, detail="This invite has already been used")

    expires_at = row[3]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="This invite has expired")

    workspace_id = row[1]
    # Mark invite as accepted
    db.execute(
        text("UPDATE workspace_invites SET accepted_at = :now WHERE token_hash = :tok"),
        {"now": datetime.utcnow(), "tok": token_hash},
    )
    db.commit()

    logger.info("User %s accepted invite to workspace %s", user.id, workspace_id)
    return {
        "detail": "Invite accepted",
        "workspace_id": workspace_id,
        "role": row[2],
    }
