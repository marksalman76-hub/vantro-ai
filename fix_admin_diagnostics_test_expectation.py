from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
TEST = ROOT / "test_admin_only_provider_diagnostics_panel.py"
PANEL = ROOT / "frontend" / "src" / "components" / "DirectMediaProviderPanel.tsx"
CLIENT_PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"admin_diagnostics_test_expectation_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

for path in [TEST]:
    if path.exists():
        (BACKUP_DIR / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

TEST.write_text(
    r'''from pathlib import Path


def test_admin_only_provider_diagnostics_panel():
    panel = Path("frontend/src/components/DirectMediaProviderPanel.tsx").read_text(encoding="utf-8")
    assert "ADMIN_ONLY_PROVIDER_DIAGNOSTICS_PANEL_V1" in panel, "admin-only diagnostics marker missing"
    assert "Advanced provider diagnostics" in panel, "diagnostics title missing"
    assert "Open diagnostics" in panel, "open diagnostics button text missing"
    assert "Generate media with selected software" not in panel, "old provider workflow title should not remain"
    assert "DirectMediaProviderPanel" in panel, "diagnostics component should still exist for admin"


def test_client_portal_provider_diagnostics_removed():
    client = Path("frontend/src/app/client/page.tsx").read_text(encoding="utf-8")
    assert "CLIENT_PORTAL_RUN_AGENT_ONLY_NO_PROVIDER_DIAGNOSTICS_V1" in client, "client removal marker missing"

    rendered_client = client.replace(
        "CLIENT_PORTAL_RUN_AGENT_ONLY_NO_PROVIDER_DIAGNOSTICS_V1: Direct provider diagnostics are intentionally not rendered in the client portal. Clients use Run Agent Task only.",
        "",
    )
    assert "DirectMediaProviderPanel" not in rendered_client, "client portal should not render provider diagnostics"


if __name__ == "__main__":
    test_admin_only_provider_diagnostics_panel()
    test_client_portal_provider_diagnostics_removed()
    print("ADMIN_ONLY_PROVIDER_DIAGNOSTICS_PANEL_TEST_PASSED")
''',
    encoding="utf-8",
)

print("ADMIN_DIAGNOSTICS_TEST_EXPECTATION_FIXED")
print(f"Backup: {BACKUP_DIR}")
print(f"Updated: {TEST}")