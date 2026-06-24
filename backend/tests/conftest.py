import sys
import os

# Guarantee backend/ is first in sys.path so `from app.X` always resolves correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Disable rate limiting before any app import so limiter is a no-op in tests
os.environ.setdefault("TESTING", "1")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool  # keeps single connection so in-memory DB persists
from fastapi.testclient import TestClient

# Import Base then ALL models in FK dependency order before create_all is called
from app.database import Base
import app.models.user  # noqa: F401
import app.models.organization  # noqa: F401
import app.models.workspace  # noqa: F401  — must come after organization (FK dep)
try:
    import app.models.agent_system  # noqa: F401 — AgentJob, PackageDownload
except Exception:  # noqa: BLE001
    pass
try:
    import app.models.refresh_token  # noqa: F401
    import app.models.audit_log  # noqa: F401
except Exception:  # noqa: BLE001
    pass
from app.models import User, Organization, Workspace, CreditsAccount, MediaJob
from app.main import app
from app.routes.auth import get_db
from app.routes import admin as _admin_mod
from app.routes import agents as _agents_mod
from app.routes import support as _support_mod
from app.routes import users as _users_mod
from app.routes import stripe as _stripe_mod
from app.routes import dashboard as _dashboard_mod
from app.routes import billing as _billing_mod

SQLALCHEMY_TEST_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_engine():
    from sqlalchemy import text as _text
    engine = create_engine(
        SQLALCHEMY_TEST_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # all sessions share one connection → same in-memory DB
    )
    Base.metadata.create_all(bind=engine)
    # Create tables defined by raw SQL migrations (not ORM models)
    with engine.connect() as conn:
        conn.execute(_text("""
            CREATE TABLE IF NOT EXISTS support_tickets (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                email TEXT,
                ticket_type TEXT,
                message TEXT,
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """))
        conn.execute(_text("""
            CREATE TABLE IF NOT EXISTS stripe_webhook_events (
                id TEXT PRIMARY KEY,
                event_type TEXT,
                processed_at TIMESTAMP
            )
        """))
        conn.commit()
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def client(db_engine):
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    for mod in (_admin_mod, _agents_mod, _support_mod, _users_mod, _stripe_mod, _dashboard_mod, _billing_mod):
        if hasattr(mod, "get_db"):
            app.dependency_overrides[mod.get_db] = override_get_db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    return {"email": "test@example.com", "password": "Test123!", "name": "Test User"}


@pytest.fixture
def registered_user(client, test_user_data):
    client.post("/api/auth/register", json=test_user_data)
    return test_user_data


@pytest.fixture
def auth_token(client, test_user_data):
    client.post("/api/auth/register", json=test_user_data)
    resp = client.post("/api/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"],
    })
    return resp.json()["access_token"]


@pytest.fixture
def authenticated_client(client, auth_token):
    client.headers["Authorization"] = f"Bearer {auth_token}"
    return client


@pytest.fixture
def valid_headers():
    return {"x-tenant-id": "test_tenant_id"}


# ── Shared helpers used by new test modules ────────────────────────────────────

@pytest.fixture
def db(db_engine):
    """Expose a live Session for tests that need direct DB access."""
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def make_user(db, *, email=None, password="Test1234!", is_admin=False):
    """Create a User + Workspace + CreditsAccount row; return (user, token, credits)."""
    import uuid as _uuid
    import hashlib as _hl
    from datetime import timedelta as _td

    uid = str(_uuid.uuid4())
    email = email or f"user-{uid[:8]}@test.com"

    from app.auth import hash_password
    from app.auth.jwt import create_access_token

    user = User(
        id=uid,
        email=email,
        password_hash=hash_password(password),
        name="Test User",
        is_active=True,
        is_admin=is_admin,
        created_at=__import__("datetime").datetime.utcnow(),
    )
    db.add(user)

    from app.models import Organization
    org = Organization(
        id=str(_uuid.uuid4()),
        name="Test Org",
        slug=f"test-org-{uid[:8]}",
        owner_id=uid,
    )
    db.add(org)

    ws = Workspace(
        id=str(_uuid.uuid4()),
        name="Test WS",
        slug=f"test-ws-{uid[:8]}",
        organization_id=org.id,
        created_at=__import__("datetime").datetime.utcnow(),
    )
    db.add(ws)

    credits = CreditsAccount(
        id=str(_uuid.uuid4()),
        workspace_id=ws.id,
        total_credits=100,
        used_credits=0,
        updated_at=__import__("datetime").datetime.utcnow(),
    )
    db.add(credits)
    db.commit()
    db.refresh(user)
    db.refresh(credits)

    token = create_access_token(uid, expires_delta=_td(hours=1))
    return user, token, credits
