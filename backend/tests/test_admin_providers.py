from fastapi import status

from conftest import make_user


def test_admin_provider_health_includes_github_connection_status(client, db):
    _, token, _ = make_user(db, email="admin-providers@test.com", is_admin=True)

    response = client.get(
        "/api/admin/providers",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    providers = response.json()["providers"]
    github = next((provider for provider in providers if provider["name"] == "GitHub"), None)

    assert github is not None
    assert github["category"] == "Code / Repository"
    assert github["role"] == "primary"
    assert github["readiness"] in {"ready", "not_configured"}
