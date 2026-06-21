from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import timedelta
from app.auth import hash_password, verify_password, create_access_token
from app.models import User
from app.database import SessionLocal
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/auth", tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=request.email, password_hash=hash_password(request.password), name=request.name)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id, expires_delta=timedelta(hours=24))
    return {"access_token": token, "user_id": user.id}

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.id, expires_delta=timedelta(hours=24))
    return {"access_token": token, "user_id": user.id}

@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}
