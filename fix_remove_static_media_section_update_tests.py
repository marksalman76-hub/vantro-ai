from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent

ADMIN_PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
REMOVE_TEST = ROOT / "test_remove_wrong_admin_complete_media_static_section.py"
RELIABILITY_TEST = ROOT / "test_universal_media_client_admin_run_agent_reliability.py"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"remove_static_media_section_update_tests_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

for path in [ADMIN_PAGE, REMOVE_TEST, RELIABILITY_TEST]:
    if path.exists():
        backup_name = str(path.relative_to(ROOT)).replace("\\", "__").replace("/", "__")
        (BACKUP_DIR / backup_name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

admin = ADMIN_PAGE.read_text(encoding="utf-8")

marker = "{/* ADMIN_RUN_AGENT_UNIVERSAL_COMPLETE_MEDIA_PANEL_V1 */}"
marker_index = admin.find(marker)

if marker_index != -1:
    section_end = admin.find("</section>", marker_index)
    if section_end == -1:
        raise SystemExit("STATIC_COMPLETE_MEDIA_SECTION_END_NOT_FOUND")

    section_end += len("</section>")

    remove_start = marker_index
    while remove_start > 0 and admin[remove_start - 1] in " \t\r\n":
        remove_start -= 1

    removed_block = admin[remove_start:section_end]

    required_terms = [
        "ADMIN_RUN_AGENT_UNIVERSAL_COMPLETE_MEDIA_PANEL_V1",
        "Admin complete media test",
        "UniversalCompleteMediaRunAgentPanel",
    ]

    missing = [term for term in required_terms if term not in removed_block]
    if missing:
        raise SystemExit("REFUSED_UNEXPECTED_BLOCK_MISSING_" + "_".join(missing))

    admin = admin[:remove_start] + "\n" + admin[section_end:]

# Remove the now-unused import only if admin no longer renders the component.
import_line = 'import UniversalCompleteMediaRunAgentPanel from "@/components/UniversalCompleteMediaRunAgentPanel";\n'
if "<UniversalCompleteMediaRunAgentPanel" not in admin:
    admin = admin.replace(import_line, "")

ADMIN_PAGE.write_text(admin, encoding="utf-8")

REMOVE_TEST.write_text(
    r'''from pathlib import Path


def test_wrong_admin_static_complete_media_section_removed():
    admin = Path("frontend/src/app/admin/page.tsx").read_text(encoding="utf-8")

    assert "ADMIN_RUN_AGENT_UNIVERSAL_COMPLETE_MEDIA_PANEL_V1" not in admin, "wrong static admin complete-media section still exists"
    assert "Admin complete media test" not in admin, "wrong static admin complete-media title still exists"
    assert "Admin-only live test path for the same one-prompt complete media workflow" not in admin, "wrong static admin text still exists"

    # Preserve working admin provider diagnostics path.
    assert "DirectMediaProviderPanel" in admin, "direct provider diagnostics component/path must remain"


if __name__ == "__main__":
    test_wrong_admin_static_complete_media_section_removed()
    print("WRONG_ADMIN_STATIC_COMPLETE_MEDIA_SECTION_REMOVED_TEST_PASSED")
''',
    encoding="utf-8",
)

RELIABILITY_TEST.write_text(
    r'''from pathlib import Path


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
''',
    encoding="utf-8",
)

print("STATIC_COMPLETE_MEDIA_SECTION_REMOVED_AND_TESTS_UPDATED")
print(f"Backup: {BACKUP_DIR}")
print(f"Updated: {ADMIN_PAGE}")
print(f"Updated: {REMOVE_TEST}")
print(f"Updated: {RELIABILITY_TEST}")