from pathlib import Path


def test_client_complete_media_run_agent_reliable():
    client = Path("frontend/src/app/client/page.tsx").read_text(encoding="utf-8")
    component = Path("frontend/src/components/UniversalCompleteMediaRunAgentPanel.tsx").read_text(encoding="utf-8")

    assert "CLIENT_RUN_AGENT_COMPLETE_MEDIA_LOCAL_STORAGE_FALLBACK_V1" in client, "client Run Agent localStorage fallback missing"
    assert "universal_complete_media_config" in client, "client Run Agent does not read media config storage"
    assert 'fetch("/api/universal-complete-media"' in client, "client Run Agent does not call complete media route"
    assert "UNIVERSAL_COMPLETE_MEDIA_LOCAL_STORAGE_BRIDGE_V1" in component, "component does not persist media config"
    assert "window.localStorage.setItem" in component, "component localStorage write missing"


def test_admin_complete_media_panel_present():
    admin = Path("frontend/src/app/admin/page.tsx").read_text(encoding="utf-8")
    assert "ADMIN_RUN_AGENT_UNIVERSAL_COMPLETE_MEDIA_PANEL_V1" in admin, "admin complete media panel missing"
    assert "UniversalCompleteMediaRunAgentPanel" in admin, "admin does not import/render complete media component"
    assert "Admin complete media test" in admin, "admin panel title missing"


if __name__ == "__main__":
    test_client_complete_media_run_agent_reliable()
    test_admin_complete_media_panel_present()
    print("UNIVERSAL_MEDIA_CLIENT_ADMIN_RUN_AGENT_RELIABILITY_TEST_PASSED")
