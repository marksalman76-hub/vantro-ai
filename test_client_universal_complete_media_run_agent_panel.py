from pathlib import Path


def test_client_universal_complete_media_panel_installed():
    client = Path("frontend/src/app/client/page.tsx").read_text(encoding="utf-8")
    component = Path("frontend/src/components/UniversalCompleteMediaRunAgentPanel.tsx").read_text(encoding="utf-8")

    assert "CLIENT_RUN_AGENT_UNIVERSAL_COMPLETE_MEDIA_PANEL_V1" in client, "client run agent marker missing"
    assert "UniversalCompleteMediaRunAgentPanel" in client, "client page does not import/render panel"
    assert "Complete media file" in component, "component title missing"
    assert "Create complete media file" in component, "generate button missing"
    assert "Age range" in component, "age control missing"
    assert "Gender presentation" in component, "gender control missing"
    assert "Ethnicity / cultural appearance" in component, "ethnicity/cultural appearance control missing"
    assert "Ultra-human likeness" in component, "avatar likeness control missing"
    assert "Facial features" in component, "facial feature control missing"
    assert "Expressions" in component, "expression control missing"
    assert "/api/universal-complete-media" in component, "client-safe universal complete media route missing"


def test_client_universal_complete_media_routes_exist():
    assert Path("frontend/src/app/api/universal-complete-media/route.ts").exists(), "complete media route missing"
    assert Path("frontend/src/app/api/universal-complete-media-status/route.ts").exists(), "status route missing"
    assert Path("frontend/src/app/api/universal-complete-media-asset/route.ts").exists(), "asset route missing"


if __name__ == "__main__":
    test_client_universal_complete_media_panel_installed()
    test_client_universal_complete_media_routes_exist()
    print("CLIENT_UNIVERSAL_COMPLETE_MEDIA_RUN_AGENT_PANEL_TEST_PASSED")
