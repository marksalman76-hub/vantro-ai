from pathlib import Path


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
