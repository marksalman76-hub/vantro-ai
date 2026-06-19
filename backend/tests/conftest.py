import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def valid_headers():
    """Standard client tenant headers."""
    return {
        "x-tenant-id": "test_tenant_001",
        "content-type": "application/json",
    }


@pytest.fixture
def owner_headers():
    """Owner/admin tenant headers."""
    return {
        "x-tenant-id": "owner_managed_test",
        "x-actor-role": "owner",
        "content-type": "application/json",
    }
