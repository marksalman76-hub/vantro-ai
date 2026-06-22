from fastapi import APIRouter
from pydantic import BaseModel
from app.services import email_service

router = APIRouter(prefix="/api", tags=["contact"])


class EnterpriseEnquiry(BaseModel):
    name: str
    company: str
    email: str
    phone: str = ""
    volume: str = ""
    message: str = ""


@router.post("/contact/enterprise")
async def enterprise_enquiry(body: EnterpriseEnquiry):
    if not body.name or not body.company or not body.email:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Name, company and email are required")

    email_service.send_enterprise_enquiry(
        name=body.name,
        company=body.company,
        email=body.email,
        phone=body.phone,
        volume=body.volume,
        message=body.message,
    )
    return {"success": True}
