from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent

TEST_CLIENT_EXECUTION = ROOT / "test_client_run_agent_complete_media_execution.py"
TEST_RELIABILITY = ROOT / "test_universal_media_client_admin_run_agent_reliability.py"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"stale_run_agent_media_popup_tests_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

for path in [TEST_CLIENT_EXECUTION, TEST_RELIABILITY]:
    if path.exists():
        backup_name = str(path.relative_to(ROOT)).replace("\\", "__").replace("/", "__")
        (BACKUP_DIR / backup_name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

TEST_CLIENT_EXECUTION.write_text(
    r'''from pathlib import Path


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
''',
    encoding="utf-8",
)

TEST_RELIABILITY.write_text(
    r'''from pathlib import Path


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
''',
    encoding="utf-8",
)

print("STALE_RUN_AGENT_MEDIA_POPUP_TESTS_FIXED")
print(f"Backup: {BACKUP_DIR}")
print(f"Updated: {TEST_CLIENT_EXECUTION}")
print(f"Updated: {TEST_RELIABILITY}")