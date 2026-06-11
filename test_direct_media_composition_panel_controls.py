from pathlib import Path


def test_composition_panel_controls_present():
    panel = Path("frontend/src/components/DirectMediaProviderPanel.tsx").read_text(encoding="utf-8")
    assert "DIRECT_MEDIA_COMPOSITION_PANEL_CONTROLS_V1" in panel, panel[:500]
    assert "Compose video + audio" in panel, panel[:500]
    assert "/api/admin-direct-media-provider-compose" in panel, panel[:500]
    assert "latestVideoJobId" in panel, panel[:500]
    assert "latestAudioJobId" in panel, panel[:500]


if __name__ == "__main__":
    test_composition_panel_controls_present()
    print("DIRECT_MEDIA_COMPOSITION_PANEL_CONTROLS_TEST_PASSED")
