import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.limiter import limiter
from app.routes.admin import router as admin_router
from app.routes.auth import router as auth_router
from app.routes.contact import router as contact_router
from app.routes.dashboard import router as dashboard_router
from app.routes.stripe import router as stripe_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Web tier has no background tasks — job processing is handled
    # exclusively by the vantro-worker ECS service via SQS.
    logger.info("Vantro API starting up")
    yield
    logger.info("Vantro API shutting down")


app = FastAPI(
    title="Vantro AI API",
    description="Enterprise AI video generation platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://vantro.ai", "https://www.vantro.ai"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(contact_router)
app.include_router(dashboard_router)
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
