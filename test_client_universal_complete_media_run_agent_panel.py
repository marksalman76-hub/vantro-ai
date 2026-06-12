from pathlib import Path


def test_client_universal_complete_media_run_agent_panel():
    client = Path("frontend/src/app/client/page.tsx").read_text(encoding="utf-8")
    component = Path("frontend/src/components/UniversalCompleteMediaRunAgentPanel.tsx").read_text(encoding="utf-8")

    assert "UniversalCompleteMediaRunAgentPanel" in client, "client Run Agent media popup component missing"
    assert "CLIENT_RUN_AGENT_COMPLETE_MEDIA_EXECUTION_V1" in client, "client Run Agent media execution marker missing"
    assert "CLIENT_RUN_AGENT_COMPLETE_MEDIA_LOCAL_STORAGE_FALLBACK_V1" in client, "client Run Agent storage fallback missing"
    assert "RUN_AGENT_MEDIA_POPUP_CONFIG_BRIDGE_V1" in component, "media popup config bridge missing"
    assert 'data-run-agent-media-popup="true"' in component, "media popup marker missing"
    assert "Create complete media file" not in component, "old separate create button should not exist"


if __name__ == "__main__":
    test_client_universal_complete_media_run_agent_panel()
    print("CLIENT_UNIVERSAL_COMPLETE_MEDIA_RUN_AGENT_PANEL_TEST_PASSED")
