import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()  # load backend/.env before any other imports read os.getenv()
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Vantro API starting up")

    # Start the agent worker background loop
    import asyncio
    from app.agents.agent_worker import run_agent_worker
    worker_task = asyncio.create_task(run_agent_worker())

    yield

    # Graceful shutdown
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
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
    allow_origins=[
        "http://localhost:3000",
        "https://vantro.ai",
        "https://www.vantro.ai",
        "https://ecommerce-ai-agent-platform-1.onrender.com",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
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


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "vantro-api"}


@app.get("/")
async def root():
    return {"name": "Vantro AI API", "version": "1.0.0", "status": "running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
