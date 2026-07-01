"""
Client Integrations API — encrypted credential storage per workspace.

Endpoints:
  GET  /api/integrations            — list connected integrations for this workspace
  POST /api/integrations/connect    — store encrypted credential
  POST /api/integrations/test       — test a stored credential (never returns raw value)
  DELETE /api/integrations/disconnect — remove a stored credential
  GET  /api/integrations/catalogue  — full catalogue of supported integrations

Security contract:
  - Raw credential values are NEVER returned in any response.
  - Only key name, present T/F, length, and redacted prefix are surfaced.
  - Credentials are encrypted at rest via Fernet (AES-128-CBC + HMAC-SHA256).
  - Decryption happens only inside the test handler, never written to logs.
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import verify_token
from app.database import SessionLocal
from app.models import User, Organization
from app.models.workspace import Workspace
from app.models.agent_system import WorkspaceIntegration
from app.services.encryption_service import encrypt, decrypt, redacted_meta

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/integrations", tags=["integrations"])
security = HTTPBearer(auto_error=False)

# ---------------------------------------------------------------------------
# Integration catalogue — all supported third-party integrations
# ---------------------------------------------------------------------------

INTEGRATION_CATALOGUE = [
    # LLM providers (client's own key — overrides platform default)
    {"key": "WORKSPACE_OPENAI_API_KEY",    "name": "OpenAI",          "category": "llm",        "description": "Use your own OpenAI API key for agent runs", "test_method": "openai"},
    {"key": "WORKSPACE_ANTHROPIC_API_KEY", "name": "Anthropic",       "category": "llm",        "description": "Use your own Anthropic API key for agent runs", "test_method": "anthropic"},
    # CRM
    {"key": "HUBSPOT_API_KEY",             "name": "HubSpot",         "category": "crm",        "description": "CRM, contacts, deal pipelines", "test_method": "http_get"},
    {"key": "SALESFORCE_ACCESS_TOKEN",     "name": "Salesforce",      "category": "crm",        "description": "CRM, sales cloud, opportunity management", "test_method": "http_get"},
    {"key": "PIPEDRIVE_API_KEY",           "name": "Pipedrive",       "category": "crm",        "description": "Sales CRM and pipeline management", "test_method": "http_get"},
    # E-commerce
    {"key": "SHOPIFY_ACCESS_TOKEN",        "name": "Shopify",         "category": "ecommerce",  "description": "Store data, products, orders, customers", "test_method": "http_get"},
    {"key": "WOOCOMMERCE_SECRET",          "name": "WooCommerce",     "category": "ecommerce",  "description": "WordPress e-commerce orders and products", "test_method": "http_get"},
    {"key": "BIGCOMMERCE_ACCESS_TOKEN",    "name": "BigCommerce",     "category": "ecommerce",  "description": "BigCommerce store management", "test_method": "http_get"},
    # Advertising
    {"key": "GOOGLE_ADS_DEVELOPER_TOKEN",  "name": "Google Ads",      "category": "ads",        "description": "Search, display, Performance Max campaigns", "test_method": "key_present"},
    {"key": "META_ACCESS_TOKEN",           "name": "Meta Ads",        "category": "ads",        "description": "Facebook and Instagram advertising", "test_method": "http_get"},
    {"key": "TIKTOK_ACCESS_TOKEN",         "name": "TikTok Ads",      "category": "ads",        "description": "TikTok for Business campaigns", "test_method": "key_present"},
    # Email marketing
    {"key": "MAILCHIMP_API_KEY",           "name": "Mailchimp",       "category": "email",      "description": "Email campaigns, lists, automations", "test_method": "http_get"},
    {"key": "KLAVIYO_API_KEY",             "name": "Klaviyo",         "category": "email",      "description": "E-commerce email and SMS marketing", "test_method": "http_get"},
    {"key": "BREVO_API_KEY",               "name": "Brevo",           "category": "email",      "description": "Email, SMS, WhatsApp marketing", "test_method": "http_get"},
    # Analytics
    {"key": "GA4_MEASUREMENT_ID",          "name": "Google Analytics","category": "analytics",  "description": "GA4 property data and events", "test_method": "key_present"},
    {"key": "MIXPANEL_PROJECT_TOKEN",      "name": "Mixpanel",        "category": "analytics",  "description": "Product analytics and user behaviour", "test_method": "key_present"},
    # Reviews / reputation
    {"key": "GMB_ACCESS_TOKEN",            "name": "Google Business", "category": "reviews",    "description": "Google My Business reviews and profile", "test_method": "http_get"},
    {"key": "TRUSTPILOT_API_KEY",          "name": "Trustpilot",      "category": "reviews",    "description": "Trustpilot reviews and reputation", "test_method": "http_get"},
    # Media providers (for ugc_media_agent)
    {"key": "ELEVENLABS_API_KEY",          "name": "ElevenLabs",      "category": "media",      "description": "AI voice synthesis and cloning", "test_method": "http_get"},
    {"key": "TAVUS_API_KEY",               "name": "Tavus",           "category": "media",      "description": "Ultra-realistic AI avatar video (Phoenix-4)", "test_method": "http_get"},
    {"key": "FAL_API_KEY",                 "name": "fal.ai (Kling)",  "category": "media",      "description": "Kling 3.0 and multi-model video generation", "test_method": "key_present"},
    {"key": "SUNO_API_KEY",                "name": "Suno",            "category": "media",      "description": "AI music generation", "test_method": "key_present"},
    {"key": "ASSEMBLYAI_API_KEY",          "name": "AssemblyAI",      "category": "media",      "description": "AI captions and audio transcription", "test_method": "http_get"},
    {"key": "HIGGSFIELD_API_KEY",          "name": "Higgsfield",      "category": "media",      "description": "UGC video generation with AI actors", "test_method": "key_present"},
]

_CATALOGUE_BY_KEY = {entry["key"]: entry for entry in INTEGRATION_CATALOGUE}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


def _safe_integration_response(integration: WorkspaceIntegration) -> dict:
    """Return safe (non-sensitive) representation of a stored integration."""
    cat_entry = _CATALOGUE_BY_KEY.get(integration.integration_key, {})
    return {
        "id": integration.id,
        "integration_key": integration.integration_key,
        "integration_name": integration.integration_name or cat_entry.get("name"),
        "category": cat_entry.get("category"),
        "description": cat_entry.get("description"),
        "is_active": integration.is_active,
        "credential_present": True,
        "credential_length": None,   # length not surfaced in list — only in connect response
        "last_tested_at": integration.last_tested_at.isoformat() if integration.last_tested_at else None,
        "last_test_status": integration.last_test_status,
        "connected_at": integration.created_at.isoformat() if integration.created_at else None,
    }


async def _test_credential(integration_key: str, raw_value: str) -> tuple[bool, str]:
    """
    Attempt a lightweight validation of the credential.
    Returns (success: bool, message: str).
    Raw value used here only; never stored or logged.
    """
    cat = _CATALOGUE_BY_KEY.get(integration_key, {})
    method = cat.get("test_method", "key_present")

    if method == "key_present":
        ok = bool(raw_value and len(raw_value) > 4)
        return ok, "Credential present and non-empty" if ok else "Credential appears empty"

    if method == "openai":
        try:
            import openai as _openai
            client = _openai.OpenAI(api_key=raw_value)
            client.models.list()
            return True, "OpenAI connection successful"
        except Exception as e:
            return False, f"OpenAI connection failed: {type(e).__name__}"

    if method == "anthropic":
        try:
            import anthropic as _anthropic
            client = _anthropic.Anthropic(api_key=raw_value)
            client.models.list()
            return True, "Anthropic connection successful"
        except Exception as e:
            return False, f"Anthropic connection failed: {type(e).__name__}"

    if method == "http_get":
        try:
            import httpx
            test_urls = {
                "HUBSPOT_API_KEY":    ("https://api.hubapi.com/crm/v3/owners/?limit=1", {"Authorization": f"Bearer {raw_value}"}),
                "MAILCHIMP_API_KEY":  (f"https://us1.api.mailchimp.com/3.0/ping", {"Authorization": f"Bearer {raw_value}"}),
                "KLAVIYO_API_KEY":    ("https://a.klaviyo.com/api/accounts/", {"Authorization": f"Klaviyo-API-Key {raw_value}", "revision": "2024-02-15"}),
                "BREVO_API_KEY":      ("https://api.brevo.com/v3/account", {"api-key": raw_value}),
                "META_ACCESS_TOKEN":  (f"https://graph.facebook.com/v19.0/me?access_token={raw_value}", {}),
                "GMB_ACCESS_TOKEN":   ("https://mybusinessaccountmanagement.googleapis.com/v1/accounts", {"Authorization": f"Bearer {raw_value}"}),
                "TRUSTPILOT_API_KEY": ("https://api.trustpilot.com/v1/business-units/find?name=test", {"apikey": raw_value}),
                "ELEVENLABS_API_KEY": ("https://api.elevenlabs.io/v1/user", {"xi-api-key": raw_value}),
                "ASSEMBLYAI_API_KEY": ("https://api.assemblyai.com/v2/transcript", {"authorization": raw_value}),
                "TAVUS_API_KEY":      ("https://tavusapi.com/v2/replicas", {"x-api-key": raw_value}),
            }
            if integration_key not in test_urls:
                return bool(raw_value), "Credential present (no live test for this provider)"
            url, headers = test_urls[integration_key]
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(url, headers=headers)
            # 401/403 = key invalid; 200/2xx or even 404/429 = key reached server
            if r.status_code in (401, 403):
                return False, f"Authentication rejected by provider (HTTP {r.status_code})"
            return True, f"Provider reached successfully (HTTP {r.status_code})"
        except Exception as e:
            return False, f"Connection error: {type(e).__name__}"

    return bool(raw_value), "Credential present"


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class ConnectRequest(BaseModel):
    integration_key: str
    credential_value: str


class DisconnectRequest(BaseModel):
    integration_key: str


class TestRequest(BaseModel):
    integration_key: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/catalogue")
async def list_catalogue():
    """Return all supported integrations with metadata. No auth required."""
    return {
        "integrations": [
            {
                "key": e["key"],
                "name": e["name"],
                "category": e["category"],
                "description": e["description"],
            }
            for e in INTEGRATION_CATALOGUE
        ],
        "total": len(INTEGRATION_CATALOGUE),
    }


@router.get("")
async def list_connected_integrations(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """List all integrations connected for this workspace. Returns safe metadata only."""
    user = _get_user(credentials, db)
    ws = _get_workspace(user, db)

    rows = (
        db.query(WorkspaceIntegration)
        .filter(
            WorkspaceIntegration.workspace_id == ws.id,
            WorkspaceIntegration.is_active == True,
        )
        .order_by(WorkspaceIntegration.created_at)
        .all()
    )
    return {
        "workspace_id": ws.id,
        "integrations": [_safe_integration_response(r) for r in rows],
        "total": len(rows),
    }


@router.post("/connect")
async def connect_integration(
    body: ConnectRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Store an encrypted credential for a third-party integration.
    The raw credential value is encrypted immediately and never stored plaintext.
    """
    user = _get_user(credentials, db)
    ws = _get_workspace(user, db)

    if body.integration_key not in _CATALOGUE_BY_KEY:
        raise HTTPException(status_code=400, detail=f"Unknown integration key: {body.integration_key}")

    raw = body.credential_value.strip()
    if not raw:
        raise HTTPException(status_code=400, detail="Credential value must not be empty")

    cat = _CATALOGUE_BY_KEY[body.integration_key]
    meta = redacted_meta(raw)
    encrypted = encrypt(raw)

    existing = (
        db.query(WorkspaceIntegration)
        .filter(
            WorkspaceIntegration.workspace_id == ws.id,
            WorkspaceIntegration.integration_key == body.integration_key,
        )
        .first()
    )
    now = datetime.utcnow()
    if existing:
        existing.encrypted_value = encrypted
        existing.is_active = True
        existing.updated_at = now
        existing.last_test_status = None
        existing.last_tested_at = None
        db.commit()
        db.refresh(existing)
        record = existing
    else:
        record = WorkspaceIntegration(
            workspace_id=ws.id,
            integration_key=body.integration_key,
            integration_name=cat["name"],
            encrypted_value=encrypted,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

    return {
        "status": "connected",
        "integration_key": body.integration_key,
        "integration_name": cat["name"],
        "category": cat["category"],
        "credential_meta": meta,
        "message": f"{cat['name']} connected. Run /test to validate the credential.",
    }


@router.post("/test")
async def test_integration(
    body: TestRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Test a stored integration credential against the provider.
    Decrypts the credential only for the duration of the test.
    The raw value is never returned or logged.
    """
    user = _get_user(credentials, db)
    ws = _get_workspace(user, db)

    record = (
        db.query(WorkspaceIntegration)
        .filter(
            WorkspaceIntegration.workspace_id == ws.id,
            WorkspaceIntegration.integration_key == body.integration_key,
            WorkspaceIntegration.is_active == True,
        )
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail=f"No active credential found for {body.integration_key}")

    try:
        raw = decrypt(record.encrypted_value)
    except Exception:
        raise HTTPException(status_code=500, detail="Credential decryption failed — reconnect this integration")

    success, message = await _test_credential(body.integration_key, raw)
    del raw  # explicit cleanup

    now = datetime.utcnow()
    record.last_tested_at = now
    record.last_test_status = "ok" if success else "failed"
    record.updated_at = now
    db.commit()

    return {
        "integration_key": body.integration_key,
        "integration_name": record.integration_name,
        "test_passed": success,
        "message": message,
        "tested_at": now.isoformat(),
    }


@router.delete("/disconnect")
async def disconnect_integration(
    body: DisconnectRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Remove a stored credential. Deletes the encrypted value from the database.
    """
    user = _get_user(credentials, db)
    ws = _get_workspace(user, db)

    record = (
        db.query(WorkspaceIntegration)
        .filter(
            WorkspaceIntegration.workspace_id == ws.id,
            WorkspaceIntegration.integration_key == body.integration_key,
        )
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail=f"No credential found for {body.integration_key}")

    integration_name = record.integration_name or body.integration_key
    db.delete(record)
    db.commit()

    return {
        "status": "disconnected",
        "integration_key": body.integration_key,
        "integration_name": integration_name,
        "message": f"{integration_name} credential removed.",
    }


# ---------------------------------------------------------------------------
# Composio MCP endpoints
# ---------------------------------------------------------------------------

class ComposioSetupRequest(BaseModel):
    api_key: str
    entity_id: str = "default"


def _upsert_integration(
    db: Session,
    workspace_id: str,
    key: str,
    name: str,
    raw_value: str,
) -> None:
    """Upsert a single WorkspaceIntegration row (encrypted)."""
    encrypted = encrypt(raw_value)
    now = datetime.utcnow()
    existing = (
        db.query(WorkspaceIntegration)
        .filter(
            WorkspaceIntegration.workspace_id == workspace_id,
            WorkspaceIntegration.integration_key == key,
        )
        .first()
    )
    if existing:
        existing.encrypted_value = encrypted
        existing.integration_name = name
        existing.is_active = True
        existing.updated_at = now
    else:
        db.add(
            WorkspaceIntegration(
                workspace_id=workspace_id,
                integration_key=key,
                integration_name=name,
                encrypted_value=encrypted,
                is_active=True,
                created_at=now,
                updated_at=now,
            )
        )
    db.commit()


@router.post("/composio", status_code=201)
async def setup_composio(
    body: ComposioSetupRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Save Composio API key (and optional entity_id) for this workspace.
    Owner or admin only.

    Validates the key against Composio before persisting.
    Returns the count of tools immediately available via connected apps.
    """
    user = _get_user(credentials, db)
    if not user.is_admin:
        # Allow workspace owners (org owners) as well as platform admins
        org = db.query(Organization).filter(Organization.owner_id == user.id).first()
        if not org:
            raise HTTPException(status_code=403, detail="Owner or admin required")

    ws = _get_workspace(user, db)

    api_key = body.api_key.strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="api_key must not be empty")

    entity_id = body.entity_id.strip() or "default"

    # Validate the key works before storing (non-fatal: store even if no apps connected yet)
    from app.services.composio_service import get_available_tools
    tools = get_available_tools(api_key, entity_id)

    # Persist both credentials
    _upsert_integration(db, ws.id, "COMPOSIO_API_KEY", "Composio API Key", api_key)
    _upsert_integration(db, ws.id, "COMPOSIO_ENTITY_ID", "Composio Entity ID", entity_id)

    return {
        "status": "configured",
        "entity_id": entity_id,
        "connected_tools": len(tools),
        "message": (
            f"Composio configured. {len(tools)} tool(s) available from connected apps. "
            "Connect apps at app.composio.dev to expand the tool set."
        ),
    }


@router.get("/composio/apps")
async def list_composio_apps(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    List the Anthropic-format tools available via this workspace's Composio account.
    Returns tool names and total count.
    """
    user = _get_user(credentials, db)
    ws = _get_workspace(user, db)

    from app.services.composio_service import get_composio_credentials, get_available_tools
    creds = get_composio_credentials(db, ws.id)
    if not creds:
        raise HTTPException(status_code=404, detail="Composio not configured for this workspace")

    api_key, entity_id = creds
    tools = get_available_tools(api_key, entity_id)

    return {
        "workspace_id": ws.id,
        "entity_id": entity_id,
        "tools": [t["name"] for t in tools],
        "count": len(tools),
    }


@router.delete("/composio", status_code=204)
async def remove_composio(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Remove Composio integration (both API key and entity_id rows).
    Owner or admin only.
    """
    user = _get_user(credentials, db)
    if not user.is_admin:
        org = db.query(Organization).filter(Organization.owner_id == user.id).first()
        if not org:
            raise HTTPException(status_code=403, detail="Owner or admin required")

    ws = _get_workspace(user, db)

    db.query(WorkspaceIntegration).filter(
        WorkspaceIntegration.workspace_id == ws.id,
        WorkspaceIntegration.integration_key.in_(["COMPOSIO_API_KEY", "COMPOSIO_ENTITY_ID"]),
    ).delete(synchronize_session=False)
    db.commit()
