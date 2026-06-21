import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, SessionLocal
from app.routes.auth import router as auth_router
from app.routes.stripe import router as stripe_router

app = FastAPI(
    title="Vantro AI API",
    description="Enterprise AI video generation platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://vantro.ai"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(stripe_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "vantro-api"}

@app.get("/")
async def root():
    return {"name": "Vantro AI API", "version": "1.0.0", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
