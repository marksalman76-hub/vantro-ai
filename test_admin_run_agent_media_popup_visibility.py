from pathlib import Path


def test_admin_media_popup_visible_for_selected_agent():
    component = Path("frontend/src/components/UniversalCompleteMediaRunAgentPanel.tsx").read_text(encoding="utf-8")

    assert "ADMIN_MEDIA_POPUP_ALWAYS_VISIBLE_FOR_SELECTED_AGENT_V1" in component, "admin visibility override marker missing"
    assert 'mode === "admin"' in component, "admin mode condition missing"
    assert "activeAgents.length > 0" in component, "admin popup must show when any agent is selected"
    assert ": activeAgents.some(isCreativeCapableAgent)" in component, "client creative-agent gate must remain"
    assert 'data-run-agent-media-popup="true"' in component, "media popup marker missing"
    assert "Create complete media when Run Agent is clicked" in component, "popup Run Agent wording missing"


if __name__ == "__main__":
    test_admin_media_popup_visible_for_selected_agent()
    print("ADMIN_RUN_AGENT_MEDIA_POPUP_VISIBILITY_TEST_PASSED")
