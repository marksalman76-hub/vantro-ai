from pathlib import Path


def test_client_complete_media_run_agent_reliable():
    client = Path("frontend/src/app/client/page.tsx").read_text(encoding="utf-8")
    component = Path("frontend/src/components/UniversalCompleteMediaRunAgentPanel.tsx").read_text(encoding="utf-8")

    assert "CLIENT_RUN_AGENT_COMPLETE_MEDIA_LOCAL_STORAGE_FALLBACK_V1" in client, "client Run Agent localStorage fallback missing"
    assert "universal_complete_media_config" in client, "client Run Agent does not read media config storage"
    assert 'fetch("/api/universal-complete-media"' in client, "client Run Agent does not call complete media route"

    assert "RUN_AGENT_MEDIA_POPUP_CONFIG_BRIDGE_V1" in component, "component popup config bridge missing"
    assert "window.localStorage.setItem" in component, "component localStorage write missing"
    assert 'data-run-agent-media-popup="true"' in component, "component popup marker missing"
    assert "Create complete media file" not in component, "old separate create media button should not exist"


def test_admin_media_popup_and_diagnostics_preserved():
    admin = Path("frontend/src/app/admin/page.tsx").read_text(encoding="utf-8")

    assert "ADMIN_RUN_AGENT_MEDIA_POPUP_V1" in admin, "admin Run Agent media popup missing"
    assert "ADMIN_RUN_AGENT_COMPLETE_MEDIA_ROUTE_V1" in admin, "admin Run Agent media route wrapper missing"
    assert 'fetch("/api/admin-universal-complete-media"' in admin, "admin must use admin universal complete media route"
    assert "onClick={runAdminAgentWithMediaOptions}" in admin, "admin Run Agent button must use media-aware wrapper"

    assert "ADMIN_RUN_AGENT_UNIVERSAL_COMPLETE_MEDIA_PANEL_V1" not in admin, "wrong static admin media section should not exist"
    assert "Admin complete media test" not in admin, "wrong static admin media title should not exist"
    assert "DirectMediaProviderPanel" in admin, "admin provider diagnostics must remain"


if __name__ == "__main__":
    test_client_complete_media_run_agent_reliable()
    test_admin_media_popup_and_diagnostics_preserved()
    print("UNIVERSAL_MEDIA_CLIENT_ADMIN_RUN_AGENT_RELIABILITY_TEST_PASSED")
