from pathlib import Path


def test_admin_universal_media_import_present():
    admin = Path("frontend/src/app/admin/page.tsx").read_text(encoding="utf-8")
    assert 'import UniversalCompleteMediaRunAgentPanel from "@/components/UniversalCompleteMediaRunAgentPanel";' in admin, "admin import missing"
    assert "ADMIN_RUN_AGENT_UNIVERSAL_COMPLETE_MEDIA_PANEL_V1" in admin, "admin universal media panel marker missing"
    assert "<UniversalCompleteMediaRunAgentPanel" in admin, "admin panel render missing"


if __name__ == "__main__":
    test_admin_universal_media_import_present()
    print("ADMIN_UNIVERSAL_MEDIA_IMPORT_TEST_PASSED")
