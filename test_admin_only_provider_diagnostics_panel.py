from pathlib import Path


def test_admin_only_provider_diagnostics_panel():
    panel = Path("frontend/src/components/DirectMediaProviderPanel.tsx").read_text(encoding="utf-8")
    assert "ADMIN_ONLY_PROVIDER_DIAGNOSTICS_PANEL_V1" in panel, "admin-only diagnostics marker missing"
    assert "Advanced provider diagnostics" in panel, "diagnostics title missing"
    assert "Open diagnostics" in panel, "open diagnostics button text missing"
    assert "if (!isAdmin) return null" in panel, "panel must be admin-only"
    assert "Generate media with selected software" not in panel, "old provider workflow title should not remain"


def test_client_portal_provider_diagnostics_removed():
    client = Path("frontend/src/app/client/page.tsx").read_text(encoding="utf-8")
    assert "CLIENT_PORTAL_RUN_AGENT_ONLY_NO_PROVIDER_DIAGNOSTICS_V1" in client, "client removal marker missing"
    assert "DirectMediaProviderPanel" not in client.replace("Direct provider diagnostics are intentionally not rendered in the client portal", ""), "client portal should not render provider diagnostics"


if __name__ == "__main__":
    test_admin_only_provider_diagnostics_panel()
    test_client_portal_provider_diagnostics_removed()
    print("ADMIN_ONLY_PROVIDER_DIAGNOSTICS_CLIENT_BUILD_FIX_TEST_PASSED")
