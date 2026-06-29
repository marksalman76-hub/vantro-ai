import json
import os
import re
import threading
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.auth import verify_token
from app.database import SessionLocal
from app.models import User

router = APIRouter(prefix="/api/admin/brand-assets", tags=["brand-assets"])
security = HTTPBearer(auto_error=False)

UPLOAD_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "uploads", "brand_assets"
)
UPLOAD_DIR = os.path.normpath(UPLOAD_DIR)
MANIFEST_PATH = os.path.join(UPLOAD_DIR, "manifest.json")
MAX_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB

ALLOWED_MIME_PREFIXES = ("image/", "video/")
ALLOWED_MIME_EXACT = {
    "application/pdf",
    "text/plain",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

_manifest_lock = threading.Lock()

os.makedirs(UPLOAD_DIR, exist_ok=True)


def _load_manifest() -> dict:
    if not os.path.exists(MANIFEST_PATH):
        return {}
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return {}


def _save_manifest(manifest: dict) -> None:
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def _sanitize_filename(name: str) -> str:
    name = name.replace(" ", "_")
    name = re.sub(r"[^A-Za-z0-9._\-]", "", name)
    return name or "file"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    admin_email = os.getenv("ADMIN_EMAIL", "")
    is_admin = getattr(user, "is_admin", False)
    email_match = admin_email and user.email.lower() == admin_email.lower()
    if not is_admin and not email_match:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.get("")
def list_assets(_user: User = Depends(_require_admin)):
    with _manifest_lock:
        manifest = _load_manifest()
    assets = sorted(
        manifest.values(),
        key=lambda e: e.get("created_at", ""),
        reverse=True,
    )
    return {"assets": assets}


@router.post("", status_code=201)
async def upload_asset(
    file: UploadFile = File(...),
    _user: User = Depends(_require_admin),
):
    mime = file.content_type or ""
    allowed = any(mime.startswith(p) for p in ALLOWED_MIME_PREFIXES) or mime in ALLOWED_MIME_EXACT
    if not allowed:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {mime}")

    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 50 MB limit")

    asset_id = str(uuid.uuid4())
    safe_name = _sanitize_filename(file.filename or "upload")
    stored_filename = f"{asset_id}_{safe_name}"
    dest = os.path.join(UPLOAD_DIR, stored_filename)

    with open(dest, "wb") as f:
        f.write(contents)

    entry = {
        "id": asset_id,
        "name": file.filename or safe_name,
        "filename": stored_filename,
        "mime_type": mime,
        "size": len(contents),
        "created_at": datetime.utcnow().isoformat(),
    }

    with _manifest_lock:
        manifest = _load_manifest()
        manifest[asset_id] = entry
        _save_manifest(manifest)

    return entry


@router.delete("/{asset_id}")
def delete_asset(asset_id: str, _user: User = Depends(_require_admin)):
    with _manifest_lock:
        manifest = _load_manifest()
        entry = manifest.get(asset_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Asset not found")
        file_path = os.path.join(UPLOAD_DIR, entry["filename"])
        if os.path.exists(file_path):
            os.remove(file_path)
        del manifest[asset_id]
        _save_manifest(manifest)
    return {"ok": True}


@router.get("/files/{filename}")
def serve_file(filename: str, _user: User = Depends(_require_admin)):
    with _manifest_lock:
        manifest = _load_manifest()

    matched = next(
        (e for e in manifest.values() if e.get("filename") == filename), None
    )
    if not matched:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(path=file_path, media_type=matched.get("mime_type"))
