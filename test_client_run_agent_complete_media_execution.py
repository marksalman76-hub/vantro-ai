from pathlib import Path


def test_run_agent_complete_media_execution_wired():
    client = Path("frontend/src/app/client/page.tsx").read_text(encoding="utf-8")
    component = Path("frontend/src/components/UniversalCompleteMediaRunAgentPanel.tsx").read_text(encoding="utf-8")

    assert "CLIENT_RUN_AGENT_COMPLETE_MEDIA_EXECUTION_V1" in client, "Run Agent complete media execution marker missing"
    assert "universalCompleteMediaConfig" in client, "shared complete media config state missing"
    assert 'fetch("/api/universal-complete-media"' in client, "Run Agent does not call complete media route"
    assert 'fetch("/api/delegated-workforce-execution"' in client, "normal delegated route must remain as fallback"
    assert "UNIVERSAL_COMPLETE_MEDIA_SHARED_STATE_V1" in component, "component shared state marker missing"
    assert "onConfigChange" in component, "component must expose config changes"


if __name__ == "__main__":
    test_run_agent_complete_media_execution_wired()
    print("CLIENT_RUN_AGENT_COMPLETE_MEDIA_EXECUTION_TEST_PASSED")
