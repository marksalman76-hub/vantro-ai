"""
Reports API — weekly AI workforce reports + team templates

Client endpoints:
  GET  /api/reports/weekly              — list my weekly reports
  GET  /api/reports/weekly/{id}         — get a specific report
  POST /api/reports/weekly/generate     — trigger a report now (for testing)
  POST /api/reports/weekly/{id}/feedback— submit rating/feedback on a report
  POST /api/reports/weekly/{id}/convert-recommendation — create a task from recommendation
  GET  /api/reports/settings            — get report notification preferences
  PUT  /api/reports/settings            — update preferences

Team templates:
  GET  /api/teams/templates             — list platform + workspace templates
  POST /api/teams/templates             — create a workspace template
  DELETE /api/teams/templates/{id}      — delete a workspace template

Admin endpoints (prefixed with /api/admin/reports/):
  GET  /api/admin/reports/weekly        — all client reports (paginated)
  POST /api/admin/reports/weekly/{id}/resend   — resend email
  POST /api/admin/reports/weekly/{id}/disable  — disable report
  POST /api/admin/reports/weekly/generate/{workspace_id} — generate for specific workspace
  GET  /api/admin/governance/matrix     — full AGENT-GOV-02 matrix
  GET  /api/admin/teams/templates       — all team templates
"""
import uuid
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import verify_token
from app.database import SessionLocal
from app.models import User, Organization
from app.models.workspace import Workspace
from app.models.reports import WeeklyReport, ReportFeedback, TeamTemplate, WorkspaceReportSettings
from app.agents.agent_registry import (
    AGENT_CATALOGUE,
    AGENT_GOVERNANCE,
    PLATFORM_TEAM_TEMPLATES,
    agents_for_package,
    normalize_agent_id,
)
from app.services.weekly_report_service import (
    generate_workspace_report,
    send_report_email,
    get_or_create_report_settings,
    VALID_RATINGS,
)
from app.limiter import limiter

logger = logging.getLogger(__name__)
router = APIRouter(tags=["reports"])
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


def _get_workspace(user: User, db: Session) -> Optional[Workspace]:
    org = db.query(Organization).filter(Organization.owner_id == user.id).first()
    if not org:
        return None
    return db.query(Workspace).filter(Workspace.organization_id == org.id).first()


def _get_admin_user(credentials: HTTPAuthorizationCredentials, db: Session) -> User:
    user = _get_user(credentials, db)
    if not getattr(user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def _serialize_report(r: WeeklyReport) -> dict:
    return {
        "id": r.id,
        "workspace_id": r.workspace_id,
        "reporting_period_start": r.reporting_period_start.isoformat() if r.reporting_period_start else None,
        "reporting_period_end": r.reporting_period_end.isoformat() if r.reporting_period_end else None,
        "executive_summary": r.executive_summary,
        "sections": r.sections or [],
        "team_sections": r.team_sections or [],
        "status": r.status,
        "delivery_status": r.delivery_status,
        "email_sent_at": r.email_sent_at.isoformat() if r.email_sent_at else None,
        "email_recipients": r.email_recipients or [],
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLIENT: Weekly reports
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/api/reports/weekly")
async def list_weekly_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(12, ge=1, le=52),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)
    ws = _get_workspace(user, db)
    if not ws:
        return {"total": 0, "skip": skip, "limit": limit, "reports": []}

    base_q = db.query(WeeklyReport).filter(WeeklyReport.workspace_id == ws.id)
    total = base_q.count()
    reports = base_q.order_by(WeeklyReport.created_at.desc()).offset(skip).limit(limit).all()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "reports": [_serialize_report(r) for r in reports],
    }


@router.get("/api/reports/weekly/latest")
async def get_latest_report(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)
    ws = _get_workspace(user, db)
    if not ws:
        raise HTTPException(status_code=404, detail="No workspace found")

    report = (
        db.query(WeeklyReport)
        .filter(WeeklyReport.workspace_id == ws.id)
        .order_by(WeeklyReport.created_at.desc())
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="No reports yet")
    return _serialize_report(report)


@router.get("/api/reports/weekly/{report_id}")
async def get_weekly_report(
    report_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)
    ws = _get_workspace(user, db)
    if not ws:
        raise HTTPException(status_code=404, detail="No workspace found")

    report = db.query(WeeklyReport).filter(
        WeeklyReport.id == report_id,
        WeeklyReport.workspace_id == ws.id,
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return _serialize_report(report)


@router.post("/api/reports/weekly/generate")
@limiter.limit("3/hour")
async def trigger_report_generation(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Manually trigger a report for the current workspace (rate-limited)."""
    user = _get_user(credentials, db)
    ws = _get_workspace(user, db)
    if not ws:
        raise HTTPException(status_code=400, detail="No workspace found")

    report = generate_workspace_report(ws.id, db)
    return {"report_id": report.id, "status": report.status, "message": "Report generated successfully"}


class FeedbackRequest(BaseModel):
    rating: str = Field(..., description="One of: useful, not_useful, too_detailed, not_detailed_enough, wrong_recommendation, do_more_like_this")
    comment: Optional[str] = Field(default=None, max_length=500)


@router.post("/api/reports/weekly/{report_id}/feedback")
async def submit_report_feedback(
    report_id: str,
    body: FeedbackRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    if body.rating not in VALID_RATINGS:
        raise HTTPException(status_code=400, detail=f"Invalid rating. Must be one of: {', '.join(sorted(VALID_RATINGS))}")

    user = _get_user(credentials, db)
    ws = _get_workspace(user, db)
    if not ws:
        raise HTTPException(status_code=404, detail="No workspace found")

    report = db.query(WeeklyReport).filter(
        WeeklyReport.id == report_id,
        WeeklyReport.workspace_id == ws.id,
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    feedback = ReportFeedback(
        id=str(uuid.uuid4()),
        report_id=report_id,
        workspace_id=ws.id,
        rating=body.rating,
        comment=body.comment,
        created_at=datetime.utcnow(),
    )
    db.add(feedback)
    db.commit()
    return {"detail": "Feedback recorded"}


class ConvertRecommendationRequest(BaseModel):
    recommendation_text: str = Field(..., max_length=500)
    agent_id: Optional[str] = Field(default=None)


@router.post("/api/reports/weekly/{report_id}/convert-recommendation")
async def convert_recommendation_to_task(
    report_id: str,
    body: ConvertRecommendationRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Convert a report recommendation into an agent job (pending submission)."""
    user = _get_user(credentials, db)
    ws = _get_workspace(user, db)
    if not ws:
        raise HTTPException(status_code=404, detail="No workspace found")

    report = db.query(WeeklyReport).filter(
        WeeklyReport.id == report_id,
        WeeklyReport.workspace_id == ws.id,
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Return the pre-filled task brief for the client to confirm before submitting
    agent_id = body.agent_id or "strategist_agent"
    norm_id = normalize_agent_id(agent_id)
    agent_meta = AGENT_CATALOGUE.get(norm_id, {})

    return {
        "action": "run_agent",
        "suggested_agent_id": norm_id,
        "suggested_agent_name": agent_meta.get("name", norm_id),
        "suggested_prompt": f"Based on last week's report recommendation: {body.recommendation_text}\n\nPlease help me act on this recommendation.",
        "source_report_id": report_id,
        "message": "Use the suggested prompt with the recommended agent to act on this recommendation",
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLIENT: Report settings
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/api/reports/settings")
async def get_report_settings(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)
    ws = _get_workspace(user, db)
    if not ws:
        raise HTTPException(status_code=404, detail="No workspace found")

    settings = get_or_create_report_settings(ws.id, db)
    return {
        "enabled": settings.enabled,
        "schedule_day": settings.schedule_day,
        "schedule_hour": settings.schedule_hour,
        "timezone": settings.timezone,
        "consolidated": settings.consolidated,
        "include_credit_summary": settings.include_credit_summary,
        "include_recommendations": settings.include_recommendations,
        "include_failures": settings.include_failures,
        "include_output_links": settings.include_output_links,
        "recipients": settings.recipients or [],
    }


class ReportSettingsUpdate(BaseModel):
    enabled: Optional[bool] = None
    schedule_day: Optional[str] = Field(default=None, pattern="^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$")
    schedule_hour: Optional[int] = Field(default=None, ge=0, le=23)
    timezone: Optional[str] = Field(default=None, max_length=50)
    consolidated: Optional[bool] = None
    include_credit_summary: Optional[bool] = None
    include_recommendations: Optional[bool] = None
    include_failures: Optional[bool] = None
    include_output_links: Optional[bool] = None
    recipients: Optional[list] = None


@router.put("/api/reports/settings")
async def update_report_settings(
    body: ReportSettingsUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)
    ws = _get_workspace(user, db)
    if not ws:
        raise HTTPException(status_code=404, detail="No workspace found")

    settings = get_or_create_report_settings(ws.id, db)
    for field, value in body.model_dump(exclude_none=True).items():
        if value is not None:
            setattr(settings, field, value)
    settings.updated_at = datetime.utcnow()
    db.commit()
    return {"detail": "Report settings updated"}


# ─────────────────────────────────────────────────────────────────────────────
# CLIENT + ADMIN: Team templates
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/api/teams/templates")
async def list_team_templates(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)
    ws = _get_workspace(user, db)
    workspace_id = ws.id if ws else None

    # Platform templates
    templates = list(PLATFORM_TEAM_TEMPLATES)

    # User-created workspace templates
    if workspace_id:
        db_templates = db.query(TeamTemplate).filter(
            TeamTemplate.workspace_id == workspace_id,
            TeamTemplate.is_platform == False,
        ).order_by(TeamTemplate.created_at.desc()).all()
        for t in db_templates:
            templates.append({
                "id": t.id,
                "name": t.name,
                "description": t.description or "",
                "lead_agent_id": t.lead_agent_id,
                "agent_ids": t.agent_ids or [],
                "min_package": t.min_package,
                "is_platform": False,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            })

    # Add agent names to each template
    def enrich(template: dict) -> dict:
        enriched = dict(template)
        enriched["agents"] = [
            {
                "id": aid,
                "name": AGENT_CATALOGUE.get(aid, {}).get("name", aid),
                "category": AGENT_CATALOGUE.get(aid, {}).get("category", ""),
                "hitl_default": AGENT_CATALOGUE.get(aid, {}).get("hitl_default", "HITL-1"),
            }
            for aid in (template.get("agent_ids") or [])
        ]
        lead = template.get("lead_agent_id")
        if lead:
            enriched["lead_agent_name"] = AGENT_CATALOGUE.get(lead, {}).get("name", lead)
        return enriched

    return {"templates": [enrich(t) for t in templates]}


class CreateTeamTemplateRequest(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    agent_ids: list = Field(..., min_length=2, max_length=10)
    lead_agent_id: Optional[str] = None


@router.post("/api/teams/templates", status_code=201)
async def create_team_template(
    body: CreateTeamTemplateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)
    ws = _get_workspace(user, db)
    if not ws:
        raise HTTPException(status_code=400, detail="No workspace found")

    # Validate agent IDs
    invalid = [aid for aid in body.agent_ids if aid not in AGENT_CATALOGUE]
    if invalid:
        raise HTTPException(status_code=400, detail=f"Unknown agent IDs: {', '.join(invalid)}")

    template = TeamTemplate(
        id=str(uuid.uuid4()),
        workspace_id=ws.id,
        name=body.name,
        description=body.description,
        agent_ids=body.agent_ids,
        lead_agent_id=body.lead_agent_id,
        is_platform=False,
        created_by=user.id,
        created_at=datetime.utcnow(),
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return {"id": template.id, "name": template.name, "message": "Team template created"}


@router.delete("/api/teams/templates/{template_id}")
async def delete_team_template(
    template_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user = _get_user(credentials, db)
    ws = _get_workspace(user, db)
    if not ws:
        raise HTTPException(status_code=404, detail="No workspace found")

    template = db.query(TeamTemplate).filter(
        TeamTemplate.id == template_id,
        TeamTemplate.workspace_id == ws.id,
        TeamTemplate.is_platform == False,
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found or cannot be deleted")

    db.delete(template)
    db.commit()
    return {"detail": "Template deleted"}


# ─────────────────────────────────────────────────────────────────────────────
# ADMIN: Report management
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/api/admin/reports/weekly")
async def admin_list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    workspace_id: Optional[str] = Query(default=None),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _get_admin_user(credentials, db)
    q = db.query(WeeklyReport)
    if workspace_id:
        q = q.filter(WeeklyReport.workspace_id == workspace_id)
    total = q.count()
    reports = q.order_by(WeeklyReport.created_at.desc()).offset(skip).limit(limit).all()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "reports": [_serialize_report(r) for r in reports],
    }


@router.post("/api/admin/reports/weekly/{report_id}/resend")
async def admin_resend_report(
    report_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _get_admin_user(credentials, db)
    report = db.query(WeeklyReport).filter(WeeklyReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    settings = db.query(WorkspaceReportSettings).filter(
        WorkspaceReportSettings.workspace_id == report.workspace_id
    ).first()
    recipients = (settings.recipients if settings else []) or []

    if not recipients:
        # Try to get owner email
        ws = db.query(Workspace).filter(Workspace.id == report.workspace_id).first()
        if ws:
            org = db.query(Organization).filter(Organization.id == ws.organization_id).first()
            if org:
                from app.models import User as _User
                owner = db.query(_User).filter(_User.id == org.owner_id).first()
                if owner:
                    recipients = [owner.email]

    if not recipients:
        raise HTTPException(status_code=400, detail="No recipients configured for this workspace")

    sent = send_report_email(report, recipients, db)
    return {"sent": sent, "recipients": recipients, "report_id": report_id}


@router.post("/api/admin/reports/weekly/{report_id}/disable")
async def admin_disable_report(
    report_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _get_admin_user(credentials, db)
    report = db.query(WeeklyReport).filter(WeeklyReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    report.disabled_by_admin = True
    report.updated_at = datetime.utcnow()
    db.commit()
    return {"detail": "Report disabled"}


@router.post("/api/admin/reports/weekly/generate/{workspace_id}")
async def admin_generate_report(
    workspace_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    _get_admin_user(credentials, db)
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    report = generate_workspace_report(workspace_id, db)
    return {"report_id": report.id, "status": report.status, "sections": len(report.sections or [])}


# ─────────────────────────────────────────────────────────────────────────────
# ADMIN: Governance matrix (AGENT-GOV-02)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/api/admin/governance/matrix")
async def get_governance_matrix(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Return AGENT-GOV-02: full governance matrix for all 27 agents."""
    _get_admin_user(credentials, db)
    matrix = []
    for agent_id, meta in AGENT_CATALOGUE.items():
        gov = AGENT_GOVERNANCE.get(agent_id, {})
        matrix.append({
            "agent_id": agent_id,
            "agent_name": meta.get("name"),
            "category": meta.get("category"),
            "min_package": meta.get("min_package"),
            "hitl_default": meta.get("hitl_default"),
            "credit_estimate": meta.get("credit_estimate"),
            "architecture": meta.get("architecture"),
            **gov,
        })
    return {
        "matrix": matrix,
        "total_agents": len(matrix),
        "platform_team_templates": PLATFORM_TEAM_TEMPLATES,
    }


@router.get("/api/admin/governance/matrix/public")
async def get_governance_matrix_public(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Client-safe subset of the governance matrix — no internal fields."""
    _get_user(credentials, db)
    return {
        "agents": [
            {
                "agent_id": aid,
                "name": meta.get("name"),
                "category": meta.get("category"),
                "team_role": AGENT_GOVERNANCE.get(aid, {}).get("team_role", "supporting"),
                "lead_agent_allowed": AGENT_GOVERNANCE.get(aid, {}).get("lead_agent_allowed", False),
                "compatible_teams": AGENT_GOVERNANCE.get(aid, {}).get("compatible_teams", []),
                "weekly_report_enabled": AGENT_GOVERNANCE.get(aid, {}).get("weekly_report_enabled", True),
                "recommendation_type": AGENT_GOVERNANCE.get(aid, {}).get("recommendation_type", "tactical"),
            }
            for aid, meta in AGENT_CATALOGUE.items()
        ],
        "platform_team_templates": PLATFORM_TEAM_TEMPLATES,
    }
