from pathlib import Path


def test_run_agent_complete_media_execution_wired():
    client = Path("frontend/src/app/client/page.tsx").read_text(encoding="utf-8")
    component = Path("frontend/src/components/UniversalCompleteMediaRunAgentPanel.tsx").read_text(encoding="utf-8")

    assert "CLIENT_RUN_AGENT_COMPLETE_MEDIA_EXECUTION_V1" in client, "client Run Agent media execution marker missing"
    assert "CLIENT_RUN_AGENT_COMPLETE_MEDIA_LOCAL_STORAGE_FALLBACK_V1" in client, "client Run Agent storage fallback missing"
    assert "universalCompleteMediaConfig" in client, "client media config state missing"
    assert 'fetch("/api/universal-complete-media"' in client, "client Run Agent does not call complete media route"

    assert "RUN_AGENT_MEDIA_POPUP_CONFIG_BRIDGE_V1" in component, "new media popup config bridge missing"
    assert 'data-run-agent-media-popup="true"' in component, "new media popup marker missing"
    assert "Create complete media when Run Agent is clicked" in component, "new Run Agent media wording missing"
    assert "Create complete media file" not in component, "old separate create button should not exist"


if __name__ == "__main__":
    test_run_agent_complete_media_execution_wired()
    print("CLIENT_RUN_AGENT_COMPLETE_MEDIA_EXECUTION_TEST_PASSED")
