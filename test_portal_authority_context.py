from backend.app.runtime.portal_authority_context import (
    build_portal_authority_context,
    enforce_execution_authority,
    redact_for_portal,
)


def main():
    admin = build_portal_authority_context({
        "portal_mode": "admin",
        "role": "owner",
        "actor_id": "owner_test",
    })

    assert admin["portal_mode"] == "admin"
    assert admin["unrestricted_execution"] is True
    assert admin["package_governed"] is False
    assert admin["credit_governed"] is False
    assert admin["approval_required"] is False
    assert admin["can_view_provider_diagnostics"] is True
    assert admin["can_retry_jobs"] is True
    assert admin["can_assign_credits"] is True
    assert admin["hide_provider_secrets"] is True

    client = build_portal_authority_context({
        "portal_mode": "client",
        "client_id": "client_test",
    })

    assert client["portal_mode"] == "client"
    assert client["unrestricted_execution"] is False
    assert client["package_governed"] is True
    assert client["credit_governed"] is True
    assert client["approval_required"] is True
    assert client["can_view_provider_diagnostics"] is False
    assert client["can_retry_jobs"] is False
    assert client["can_assign_credits"] is False
    assert client["client_safe_output_only"] is True

    admin_decision = enforce_execution_authority({"owner_approval_required": True}, admin)
    assert admin_decision["allowed"] is True
    assert admin_decision["requires_credit_check"] is False
    assert admin_decision["requires_package_check"] is False
    assert admin_decision["requires_owner_approval"] is False

    client_decision = enforce_execution_authority({"owner_approval_required": True}, client)
    assert client_decision["allowed"] is True
    assert client_decision["requires_credit_check"] is True
    assert client_decision["requires_package_check"] is True
    assert client_decision["requires_owner_approval"] is True

    payload = {
        "status": "completed",
        "api_key": "secret-value",
        "provider_diagnostics": {"runway": "details"},
        "raw_provider_error": "debug error",
        "asset_url": "https://example.com/final.mp4",
    }

    admin_view = redact_for_portal(payload, admin)
    assert admin_view["api_key"] == "[redacted]"
    assert "provider_diagnostics" in admin_view
    assert "raw_provider_error" in admin_view

    client_view = redact_for_portal(payload, client)
    assert client_view["api_key"] == "[redacted]"
    assert "provider_diagnostics" not in client_view
    assert "raw_provider_error" not in client_view
    assert client_view["asset_url"] == "https://example.com/final.mp4"
    assert client_view["credential_values_exposed"] is False

    print("PORTAL_AUTHORITY_CONTEXT_TEST_PASSED")
    print("admin_reason:", admin_decision["reason"])
    print("client_reason:", client_decision["reason"])


if __name__ == "__main__":
    main()
