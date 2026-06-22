import sys
import os

# Guarantee backend/ is first in sys.path so `from app.X` always resolves correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

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
from app.models import User, Organization, Workspace, CreditsAccount, MediaJob
from app.main import app
from app.routes.auth import get_db

SQLALCHEMY_TEST_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_engine():
    engine = create_engine(
        SQLALCHEMY_TEST_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # all sessions share one connection → same in-memory DB
    )
    Base.metadata.create_all(bind=engine)
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
