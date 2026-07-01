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


def test_admin_stats_reports_unlimited_owner_credits(client, db):
    _, token, credits = make_user(db, email="admin-stats@test.com", is_admin=True)
    credits.total_credits = 100
    credits.used_credits = 100
    db.commit()

    response = client.get(
        "/api/admin/stats",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["credits_unlimited"] is True
    assert body["credit_label"] == "Unlimited"
    assert body["tier"] == "enterprise"
    assert body["package"] == "Enterprise"
    assert body["billing_mode"] == "owner_admin_unlimited"
    assert body["remaining_credits"] is None
    assert body["total_credits"] is None
    assert body["used_credits"] == credits.used_credits


def test_admin_provider_health_includes_creative_routes_without_credentials(client, db, monkeypatch):
    monkeypatch.setenv("KLING_ACCESS_KEY", "test-access-key")
    monkeypatch.setenv("KLING_SECRET_KEY", "test-secret-key")
    _, token, _ = make_user(db, email="admin-creative-providers@test.com", is_admin=True)

    response = client.get(
        "/api/admin/providers",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    providers = body["providers"]
    provider_names = {provider["name"] for provider in providers}

    assert "Kling" in provider_names
    assert body["creative_provider_routing"]["providers"]["kling"]["models"] == [
        "Kling 3.0 Turbo",
        "Kling 3.0",
        "Cinema Studio 4K",
    ]
    assert body["creative_provider_routing"]["providers"]["openai_dalle"]["models"] == [
        "DALL-E 3",
        "DALL-E 3 HD",
    ]
    assert body["provider_stack"]["providers"]["kling"]["configured"] is True
    assert body["credential_values_exposed"] is False
