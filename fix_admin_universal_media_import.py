from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
ADMIN_PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
TEST = ROOT / "test_admin_universal_media_import.py"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"admin_universal_media_import_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

for path in [ADMIN_PAGE, TEST]:
    if path.exists():
        backup_name = str(path.relative_to(ROOT)).replace("\\", "__").replace("/", "__")
        (BACKUP_DIR / backup_name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

admin = ADMIN_PAGE.read_text(encoding="utf-8")

import_line = 'import UniversalCompleteMediaRunAgentPanel from "@/components/UniversalCompleteMediaRunAgentPanel";'

if import_line not in admin:
    lines = admin.splitlines()
    insert_index = None

    for index, line in enumerate(lines):
        if line.strip().startswith("import "):
            insert_index = index + 1

    if insert_index is None:
        for index, line in enumerate(lines):
            if line.strip() in ['"use client";', "'use client';"]:
                insert_index = index + 1
                break

    if insert_index is None:
        insert_index = 0

    lines.insert(insert_index, import_line)
    admin = "\n".join(lines) + "\n"

ADMIN_PAGE.write_text(admin, encoding="utf-8")

TEST.write_text(
    r'''from pathlib import Path


def test_admin_universal_media_import_present():
    admin = Path("frontend/src/app/admin/page.tsx").read_text(encoding="utf-8")
    assert 'import UniversalCompleteMediaRunAgentPanel from "@/components/UniversalCompleteMediaRunAgentPanel";' in admin, "admin import missing"
    assert "ADMIN_RUN_AGENT_UNIVERSAL_COMPLETE_MEDIA_PANEL_V1" in admin, "admin universal media panel marker missing"
    assert "<UniversalCompleteMediaRunAgentPanel" in admin, "admin panel render missing"


if __name__ == "__main__":
    test_admin_universal_media_import_present()
    print("ADMIN_UNIVERSAL_MEDIA_IMPORT_TEST_PASSED")
''',
    encoding="utf-8",
)

print("ADMIN_UNIVERSAL_MEDIA_IMPORT_FIXED")
print(f"Backup: {BACKUP_DIR}")
print(f"Updated: {ADMIN_PAGE}")
print(f"Created: {TEST}")