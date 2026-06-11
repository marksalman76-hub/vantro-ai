from pathlib import Path


def test_client_complete_media_run_agent_reliable():
    client = Path("frontend/src/app/client/page.tsx").read_text(encoding="utf-8")
    component = Path("frontend/src/components/UniversalCompleteMediaRunAgentPanel.tsx").read_text(encoding="utf-8")

    assert "CLIENT_RUN_AGENT_COMPLETE_MEDIA_LOCAL_STORAGE_FALLBACK_V1" in client, "client Run Agent localStorage fallback missing"
    assert "universal_complete_media_config" in client, "client Run Agent does not read media config storage"
    assert 'fetch("/api/universal-complete-media"' in client, "client Run Agent does not call complete media route"
    assert "UNIVERSAL_COMPLETE_MEDIA_LOCAL_STORAGE_BRIDGE_V1" in component, "component does not persist media config"
    assert "window.localStorage.setItem" in component, "component localStorage write missing"


def test_admin_wrong_static_complete_media_removed_but_diagnostics_preserved():
    admin = Path("frontend/src/app/admin/page.tsx").read_text(encoding="utf-8")

    assert "ADMIN_RUN_AGENT_UNIVERSAL_COMPLETE_MEDIA_PANEL_V1" not in admin, "wrong static admin complete-media panel should not exist"
    assert "Admin complete media test" not in admin, "wrong static admin complete-media title should not exist"
    assert "DirectMediaProviderPanel" in admin, "admin provider diagnostics must remain"


if __name__ == "__main__":
    test_client_complete_media_run_agent_reliable()
    test_admin_wrong_static_complete_media_removed_but_diagnostics_preserved()
    print("UNIVERSAL_MEDIA_CLIENT_ADMIN_RUN_AGENT_RELIABILITY_TEST_PASSED")
