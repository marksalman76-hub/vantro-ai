import logging
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()  # load backend/.env before any other imports read os.getenv()

_SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if _SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        sentry_sdk.init(
            dsn=_SENTRY_DSN,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
                LoggingIntegration(level=logging.WARNING, event_level=logging.ERROR),
            ],
            traces_sample_rate=0.2,
            profiles_sample_rate=0.1,
            environment=os.getenv("ENVIRONMENT", "production"),
            release=os.getenv("APP_VERSION", "1.0.0"),
            send_default_pii=False,
        )
    except ImportError:
        logging.warning("sentry-sdk not installed; install sentry-sdk[fastapi] to enable error tracking")
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.limiter import limiter
from app.routes.admin import router as admin_router
from app.routes.agents import router as agents_router
from app.routes.auth import router as auth_router
from app.routes.contact import router as contact_router
from app.routes.dashboard import router as dashboard_router
from app.routes.stripe import router as stripe_router
from app.routes.users import router as users_router
from app.routes.support import router as support_router
from app.routes.workspaces import router as workspaces_router
from app.routes.reports import router as reports_router
from app.routes.integrations import router as integrations_router
from app.routes.billing import router as billing_router
from app.routes.api_v1 import router as api_v1_router
from app.routes.platform import router as platform_router
from app.routes.brand_assets import router as brand_assets_router

logger = logging.getLogger(__name__)

RATE_LIMITS = {
    "global": "200/minute",
    "login": "10/minute",
    "media_generation": "5/minute",
    "billing": "20/minute",
}


async def cost_protection_middleware(request: Request, call_next) -> Response:
    response = await call_next(request)
    return response


class APIVersionMiddleware(BaseHTTPMiddleware):
    """Transparently rewrite /api/v1/* → /api/* so clients can adopt versioned paths."""
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path.startswith("/api/v1/"):
            scope = dict(request.scope)
            new_path = request.url.path.replace("/api/v1/", "/api/", 1)
            scope["path"] = new_path
            scope["raw_path"] = new_path.encode()
            request = Request(scope, request.receive, request.send)
        return await call_next(request)


_CSRF_EXEMPT_PATHS = {"/health", "/health/ready", "/api/stripe/webhook", "/api/auth/login", "/api/auth/register", "/api/auth/forgot-password", "/api/auth/reset-password", "/api/auth/login/", "/api/auth/register/", "/api/auth/forgot-password/", "/api/auth/reset-password/"}
_CSRF_SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
_IS_PROD_CSRF = os.getenv("ENVIRONMENT", "production") == "production"
_CSRF_DISABLED = os.getenv("TESTING", "0") == "1"  # bypass in automated tests


class CSRFMiddleware(BaseHTTPMiddleware):
    """Double-submit cookie CSRF protection.

    - Safe methods (GET/HEAD/OPTIONS) pass through; on GET 200 responses a
      csrf_token cookie is set so JS can read it.
    - Mutating methods require X-CSRF-Token header to match the csrf_token cookie.
    - Stripe webhook and health paths are exempt.
    - Disabled entirely when TESTING=1 (automated test environment).
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        import secrets

        # Skip CSRF enforcement in the test environment
        if _CSRF_DISABLED:
            return await call_next(request)

        path = request.url.path
        method = request.method.upper()

        # Bypass CSRF for all auth endpoints - they're unauthenticated
        if "/auth/" in path:
            return await call_next(request)

        # Exempt paths and safe methods
        if path in _CSRF_EXEMPT_PATHS or method in _CSRF_SAFE_METHODS:
            response = await call_next(request)
            # On GET 200, ensure csrf_token cookie is set
            if method == "GET" and response.status_code == 200:
                if not request.cookies.get("csrf_token"):
                    token = secrets.token_hex(32)
                    response.set_cookie(
                        key="csrf_token",
                        value=token,
                        httponly=False,  # JS must read it
                        samesite="strict",
                        secure=_IS_PROD_CSRF,
                        max_age=3600,
                    )
            return response

        # Mutating request — validate CSRF token
        cookie_token = request.cookies.get("csrf_token", "")
        header_token = request.headers.get("X-CSRF-Token", "")

        if not cookie_token or not header_token or not secrets.compare_digest(cookie_token, header_token):
            from fastapi.responses import JSONResponse as _JSONResponse
            return _JSONResponse(
                status_code=403,
                content={"detail": "CSRF validation failed"},
            )

        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Remove headers that reveal the tech stack
        for _h in ("Server", "X-Powered-By"):
            try:
                del response.headers[_h]
            except KeyError:
                pass
        # Harden response posture
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none'"
        )
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Vantro API starting up")

    # Register platform creative providers (HeyGen, ElevenLabs, Runway, etc.)
    # Run as background task to avoid blocking startup
    def init_providers_sync():
        from app.providers import init_providers
        init_providers()

    import threading
    threading.Thread(target=init_providers_sync, daemon=True).start()

    # Start the agent worker background loop.
    # Skipped in test mode, and when DISABLE_INLINE_WORKER=1 (dedicated ECS service handles it).
    import asyncio
    _testing = os.getenv("TESTING", "0") == "1"
    _external_worker = os.getenv("DISABLE_INLINE_WORKER", "0") == "1"
    if not _testing and not _external_worker:
        from app.agents.agent_worker import run_agent_worker
        worker_task = asyncio.create_task(run_agent_worker())
    else:
        if _external_worker:
            logger.info("Inline agent worker disabled — dedicated worker ECS service is active")
        worker_task = None

    yield

    # Graceful shutdown
    if worker_task is not None:
        worker_task.cancel()
    try:
        if worker_task is not None:
            await worker_task
    except asyncio.CancelledError:
        pass
    logger.info("Vantro API shutting down")


_IS_PROD = os.getenv("ENVIRONMENT", "production") == "production"

app = FastAPI(
    title="Vantro AI API",
    description="Enterprise AI video generation platform",
    version="1.0.0",
    lifespan=lifespan,
    # Disable interactive API docs in production — they expose route schemas and framework info
    docs_url=None if _IS_PROD else "/docs",
    redoc_url=None if _IS_PROD else "/redoc",
    openapi_url=None if _IS_PROD else "/openapi.json",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ── Generic error handlers — never leak stack traces or framework details to clients ──

from fastapi import Request as _Request
from fastapi.responses import JSONResponse as _JSONResponse
from fastapi.exceptions import RequestValidationError as _RequestValidationError
from starlette.exceptions import HTTPException as _StarletteHTTPException


@app.exception_handler(_StarletteHTTPException)
async def _http_exception_handler(request: _Request, exc: _StarletteHTTPException):
    return _JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(_RequestValidationError)
async def _validation_exception_handler(request: _Request, exc: _RequestValidationError):
    # Return a generic 422 — don't expose Pydantic field paths to clients
    return _JSONResponse(
        status_code=422,
        content={"detail": "Invalid request data"},
    )


@app.exception_handler(Exception)
async def _generic_exception_handler(request: _Request, exc: Exception):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return _JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred"},
    )
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFMiddleware)
app.add_middleware(APIVersionMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://vantro.ai",
        "https://www.vantro.ai",
    ],
    allow_origin_regex=r"https://vantro-.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)
app.include_router(agents_router)
app.include_router(auth_router)
app.include_router(contact_router)
app.include_router(dashboard_router)
app.include_router(stripe_router)
app.include_router(users_router)
app.include_router(support_router)
app.include_router(workspaces_router)
app.include_router(reports_router)
app.include_router(integrations_router)
app.include_router(billing_router)
app.include_router(api_v1_router)
app.include_router(platform_router)
app.include_router(brand_assets_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "vantro-api", "version": os.getenv("APP_VERSION", "1.0.0")}


@app.get("/health/ready")
async def readiness_probe():
    """ECS/Kubernetes readiness probe — verifies DB and key dependencies."""
    import time
    from fastapi.responses import JSONResponse
    from sqlalchemy import text as _text
    from app.database import SessionLocal

    checks: dict[str, str] = {}
    healthy = True

    # DB check
    try:
        db = SessionLocal()
        db.execute(_text("SELECT 1"))
        db.close()
        checks["database"] = "ok"
    except Exception as exc:
        checks["database"] = f"error: {exc}"
        healthy = False

    # Redis check (optional — skip if not configured)
    _redis_url = os.getenv("REDIS_URL", "")
    if _redis_url:
        try:
            import redis as _redis
            r = _redis.from_url(_redis_url, socket_connect_timeout=1)
            r.ping()
            checks["redis"] = "ok"
        except Exception as exc:
            checks["redis"] = f"error: {exc}"
    else:
        checks["redis"] = "not_configured"

    status_code = 200 if healthy else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if healthy else "not_ready",
            "checks": checks,
            "timestamp": time.time(),
        },
    )


@app.get("/")
async def root():
    return {"name": "Vantro AI API", "version": "1.0.0", "status": "running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
