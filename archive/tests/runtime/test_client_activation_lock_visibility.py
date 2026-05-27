from pathlib import Path

text = Path("frontend/src/app/client/page.tsx").read_text(encoding="utf-8")

assert "activationLocked" in text
assert "entitlementHydrated" in text
assert "postActivationChangesBlocked" in text
assert "ownerAdminReviewRequiredForChanges" in text
assert "AGENTS LOCKED" in text
assert "RESTORED" in text
assert "CHANGES REQUIRE APPROVAL" in text

print("CLIENT_ACTIVATION_LOCK_VISIBILITY_TESTS_PASSED")
print("activation_locked_visible", "AGENTS LOCKED" in text)
print("restore_status_visible", "RESTORED" in text)
print("approval_visibility", "CHANGES REQUIRE APPROVAL" in text)
