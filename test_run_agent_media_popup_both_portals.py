from pathlib import Path


def test_component_is_popup_not_separate_generator():
    component = Path("frontend/src/components/UniversalCompleteMediaRunAgentPanel.tsx").read_text(encoding="utf-8")

    assert "RUN_AGENT_MEDIA_POPUP_CONFIG_BRIDGE_V1" in component, "popup config bridge missing"
    assert 'data-run-agent-media-popup="true"' in component, "popup marker missing"
    assert "Create complete media when Run Agent is clicked" in component, "Run Agent media wording missing"
    assert "click the main <strong>Run Agent</strong> button" in component, "main Run Agent instruction missing"
    assert 'fetch("/api/universal-complete-media"' not in component, "component must not directly execute client media route"
    assert "Create complete media file" not in component, "separate create button must be removed"


def test_admin_run_agent_uses_media_popup_and_admin_route():
    admin = Path("frontend/src/app/admin/page.tsx").read_text(encoding="utf-8")

    assert "ADMIN_RUN_AGENT_MEDIA_POPUP_V1" in admin, "admin media popup not inserted into Run Agent section"
    assert "ADMIN_RUN_AGENT_COMPLETE_MEDIA_ROUTE_V1" in admin, "admin Run Agent media route wrapper missing"
    assert 'fetch("/api/admin-universal-complete-media"' in admin, "admin Run Agent must use admin media route"
    assert "onClick={runAdminAgentWithMediaOptions}" in admin, "admin Run Agent button not wired to media-aware wrapper"
    assert "<DirectMediaProviderPanel mode=\"admin\" />" in admin, "provider diagnostics must remain untouched"


if __name__ == "__main__":
    test_component_is_popup_not_separate_generator()
    test_admin_run_agent_uses_media_popup_and_admin_route()
    print("RUN_AGENT_MEDIA_POPUP_BOTH_PORTALS_TEST_PASSED")
