"""Public + client-facing platform routes: announcements, agent changelogs, system status."""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.auth import verify_token
from app.database import SessionLocal
from app.models import User, Announcement, AgentChangelog, SystemStatus
from app.models.workspace import Workspace

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/platform", tags=["platform"])
security = HTTPBearer(auto_error=False)

DEFAULT_COMPONENTS = [
    {"name": "Agent Execution", "status": "operational", "description": ""},
    {"name": "Media Generation", "status": "operational", "description": ""},
    {"name": "API",             "status": "operational", "description": ""},
    {"name": "Billing",         "status": "operational", "description": ""},
    {"name": "Reports",         "status": "operational", "description": ""},
    {"name": "File Storage",    "status": "operational", "description": ""},
]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_workspace_tier(credentials, db: Session) -> str:
    """Returns client's tier or 'all' if unauthenticated/unknown."""
    if not credentials:
        return "all"
    try:
        payload = verify_token(credentials.credentials)
        if not payload:
            return "all"
        user = db.query(User).filter(User.id == payload.get("sub")).first()
        if not user:
            return "all"
        ws = db.query(Workspace).filter(
            Workspace.organization_id == user.organization_id
        ).first()
        return ws.subscription_tier if ws and ws.subscription_tier else "all"
    except Exception:
        return "all"


# ---------------------------------------------------------------------------
# System status — public (no auth required for /api/platform/status)
# ---------------------------------------------------------------------------

@router.get("/status")
async def get_public_status(db: Session = Depends(get_db)):
    row = db.query(SystemStatus).filter(SystemStatus.id == 1).first()
    if not row:
        return {
            "overall": "operational",
            "message": None,
            "components": DEFAULT_COMPONENTS,
            "updated_at": None,
        }
    return {
        "overall": row.overall,
        "message": row.message,
        "components": row.components or DEFAULT_COMPONENTS,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


# ---------------------------------------------------------------------------
# Announcements — client-facing (filtered to tier + active + not expired)
# ---------------------------------------------------------------------------

@router.get("/announcements")
async def get_client_announcements(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    tier = _get_workspace_tier(credentials, db)
    now = datetime.utcnow()

    rows = (
        db.query(Announcement)
        .filter(
            Announcement.active == True,
            (Announcement.expires_at == None) | (Announcement.expires_at > now),
            (Announcement.target_tier == "all") | (Announcement.target_tier == tier),
        )
        .order_by(Announcement.created_at.desc())
        .limit(5)
        .all()
    )

    return [
        {
            "id": a.id,
            "title": a.title,
            "body": a.body,
            "affects": a.affects,
            "type": a.type,
            "show_as": a.show_as,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in rows
    ]


# ---------------------------------------------------------------------------
# Agent changelogs — client-facing (latest 3 per agent, or all for one agent)
# ---------------------------------------------------------------------------

@router.get("/agent-changelogs")
async def get_agent_changelogs(
    agent_id: str = Query(None),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    q = db.query(AgentChangelog)
    if agent_id:
        q = q.filter(AgentChangelog.agent_id == agent_id)
    rows = q.order_by(AgentChangelog.release_date.desc()).limit(50).all()

    return [
        {
            "id": c.id,
            "agent_id": c.agent_id,
            "agent_name": c.agent_name,
            "version": c.version,
            "summary": c.summary,
            "changes": c.changes or [],
            "affects": c.affects,
            "release_date": c.release_date.isoformat() if c.release_date else None,
        }
        for c in rows
    ]
