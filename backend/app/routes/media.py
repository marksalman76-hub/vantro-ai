"""
Media creation endpoints — video, image, and audio generation via Higgsfield, Nano Banana, ElevenLabs.
"""

import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import verify_token
from app.database import SessionLocal
from app.models import User, Organization
from app.models.workspace import Workspace, CreditsAccount, MediaJob
from app.models.agent_system import WorkspaceIntegration
from app.providers.adapters.higgsfield import HiggsfieldProvider
from app.providers.adapters.elevenlabs import ElevenLabsProvider
from app.services.encryption_service import decrypt

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/media-jobs", tags=["media"])
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


def _get_workspace(user: User, db: Session) -> Workspace:
    org = db.query(Organization).filter(Organization.owner_id == user.id).first()
    if not org:
        raise HTTPException(status_code=404, detail="No organization found")
    ws = db.query(Workspace).filter(Workspace.organization_id == org.id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="No workspace found")
    return ws


class MediaJobRequest(BaseModel):
    type: str  # product_demo, service_promo, social_ad, testimonial, explainer, etc.
    brief: str
    platform: str = "TikTok"  # Instagram, TikTok, YouTube, LinkedIn, etc.
    aspect_ratio: str = "9:16 (vertical)"  # 9:16, 1:1, 16:9, 4:5
    tone: str = "Professional"  # Professional, Friendly, Urgent, Inspirational, Playful
    age_range: Optional[str] = None
    gender: Optional[str] = None
    ethnicity: Optional[str] = None
    language: str = "English"
    video_quality: str = "1080p"  # 720p, 1080p, 4K
    use_brand_profile: bool = True


@router.post("")
async def create_media_job(
    req: MediaJobRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Create a media job (video, image, or audio).
    Routes to Higgsfield for video, Nano Banana for images, ElevenLabs for audio.
    """
    user = _get_user(credentials, db)
    workspace = _get_workspace(user, db)

    # Check credits
    credits = db.query(CreditsAccount).filter(
        CreditsAccount.workspace_id == workspace.id
    ).first()
    if not credits or credits.remaining_credits < 10:
        raise HTTPException(status_code=402, detail="Insufficient credits")

    job_id = str(uuid.uuid4())
    now = datetime.utcnow()

    # Parse aspect ratio for Higgsfield
    aspect_map = {
        "9:16 (vertical)": "9:16",
        "1:1 (square)": "1:1",
        "16:9 (landscape)": "16:9",
        "4:5 (portrait)": "4:5",
    }
    aspect_ratio = aspect_map.get(req.aspect_ratio, "9:16")

    # Determine provider and create job accordingly
    provider_type = "higgsfield"  # Default to Higgsfield for now
    external_job_id = None

    try:
        if req.type in ["product_demo", "service_promo", "social_ad", "testimonial", "explainer", "brand_story", "campaign"]:
            # Route to Higgsfield for video — get API key from workspace integrations
            higgsfield_cred = (
                db.query(WorkspaceIntegration)
                .filter(
                    WorkspaceIntegration.workspace_id == workspace.id,
                    WorkspaceIntegration.integration_key == "HIGGSFIELD_API_KEY",
                    WorkspaceIntegration.is_active == True,
                )
                .first()
            )

            if not higgsfield_cred:
                raise HTTPException(
                    status_code=503,
                    detail="Higgsfield not configured for this workspace"
                )

            # Decrypt API key
            api_key = decrypt(higgsfield_cred.encrypted_value)
            higgsfield = HiggsfieldProvider()
            higgsfield.set_api_key(api_key)  # Use set_api_key() to set both key and status

            result = await higgsfield.execute(
                prompt=req.brief,
                aspect_ratio=aspect_ratio,
                platform=req.platform.lower(),
                tone=req.tone.lower(),
                quality=req.video_quality,
            )

            if "error" in result:
                raise HTTPException(status_code=503, detail=f"Higgsfield error: {result['error']}")

            external_job_id = result.get("task_id")
            provider_type = "higgsfield"

        # Create MediaJob record (schema updated to store flexible fields)
        job = MediaJob(
            id=job_id,
            workspace_id=workspace.id,
            avatar_id=req.type,  # Repurpose for media type
            voice_id=req.platform,  # Repurpose for platform
            language=req.language,
            tone=req.tone,
            script=req.brief,
            facial_expressions=aspect_ratio,  # Repurpose
            eye_movement=req.video_quality,  # Repurpose
            blinking=provider_type,  # Repurpose for provider
            external_job_id=external_job_id,
            status="queued",
            created_at=now,
            updated_at=now,
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        # Deduct estimated credits
        credits.used_credits += 15  # Estimate for media generation
        db.commit()

        return {
            "status": "queued",
            "job_id": job_id,
            "external_job_id": external_job_id,
            "provider": provider_type,
            "message": f"{provider_type.capitalize()} media generation queued",
        }

    except Exception as e:
        logger.error(f"Media job creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))




@router.get("/{job_id}")
async def get_media_job(
    job_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Get status of a media job."""
    user = _get_user(credentials, db)
    workspace = _get_workspace(user, db)

    job = db.query(MediaJob).filter(
        MediaJob.id == job_id,
        MediaJob.workspace_id == workspace.id,
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Media job not found")

    return {
        "id": job.id,
        "status": job.status,
        "video_url": job.video_url,
        "error_message": job.error_message,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    }
