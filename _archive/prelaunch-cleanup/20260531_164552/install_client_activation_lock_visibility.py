from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"client_activation_lock_visibility_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

page_path = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
test_path = ROOT / "test_client_activation_lock_visibility.py"

backup = BACKUP_DIR / page_path.relative_to(ROOT)
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(page_path.read_text(encoding="utf-8"), encoding="utf-8")

text = page_path.read_text(encoding="utf-8")

marker = '''  const accountStatus = account?.status || "active";
'''
insert = '''  const activationLocked = Boolean(accountAny?.activation_locked);
  const entitlementHydrated = Boolean(accountAny?.entitlement_hydrated);
  const postActivationChangesBlocked = Boolean(accountAny?.post_activation_client_changes_blocked);
  const ownerAdminReviewRequiredForChanges = Boolean(accountAny?.owner_admin_required_for_post_activation_changes);
'''

if marker not in text:
    raise RuntimeError("Account status marker not found.")

if "const activationLocked = Boolean(accountAny?.activation_locked);" not in text:
    text = text.replace(marker, marker + insert, 1)

old = '''            <button
              aria-label="Notifications"
'''

new = '''            <div
              title="Activation entitlement state"
              style={{
                background: darkModeEnabled ? "rgba(15,23,42,.92)" : "#fff",
                borderRadius: 16,
                padding: "9px 14px",
                border: darkModeEnabled ? "1px solid rgba(99,102,241,.38)" : "1px solid #e5eaf2",
                fontWeight: 850,
                boxShadow: darkModeEnabled ? "0 0 0 1px rgba(99,102,241,.10), 0 12px 34px rgba(0,0,0,.24)" : "0 8px 22px rgba(15,23,42,.045)",
                color: darkModeEnabled ? "#eef2ff" : "var(--color-dark)",
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                minHeight: 34,
                whiteSpace: "nowrap",
                fontSize: 12,
              }}
            >
              <span>{activationLocked ? "🔒" : "🔓"}</span>
              <span>
                {activationLocked ? "AGENTS LOCKED" : "AGENTS UNLOCKED"}
              </span>
              <span
                style={{
                  width: 7,
                  height: 7,
                  borderRadius: 999,
                  background: entitlementHydrated ? "#22c55e" : "#f59e0b",
                  boxShadow: entitlementHydrated ? "0 0 12px rgba(34,197,94,.55)" : "0 0 12px rgba(245,158,11,.45)",
                }}
              />
              <span style={{ opacity: 0.78 }}>
                {entitlementHydrated ? "RESTORED" : "PENDING"}
              </span>
            </div>

            {postActivationChangesBlocked && (
              <div
                title="Post-activation changes require owner/admin review"
                style={{
                  background: darkModeEnabled ? "rgba(76,29,149,.28)" : "#f5f3ff",
                  borderRadius: 16,
                  padding: "9px 14px",
                  border: darkModeEnabled ? "1px solid rgba(167,139,250,.36)" : "1px solid #ddd6fe",
                  fontWeight: 850,
                  boxShadow: darkModeEnabled ? "0 0 0 1px rgba(167,139,250,.10), 0 12px 34px rgba(0,0,0,.22)" : "0 8px 22px rgba(15,23,42,.04)",
                  color: darkModeEnabled ? "#f5f3ff" : "#4c1d95",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 8,
                  minHeight: 34,
                  whiteSpace: "nowrap",
                  fontSize: 12,
                }}
              >
                <span>🛡️</span>
                <span>{ownerAdminReviewRequiredForChanges ? "CHANGES REQUIRE APPROVAL" : "CHANGE PROTECTED"}</span>
              </div>
            )}

            <button
              aria-label="Notifications"
'''

if old not in text:
    raise RuntimeError("Notifications button marker not found.")

if "AGENTS LOCKED" not in text:
    text = text.replace(old, new, 1)

page_path.write_text(text, encoding="utf-8")

test_path.write_text(
'''from pathlib import Path

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
''',
encoding="utf-8"
)

print("CLIENT_ACTIVATION_LOCK_VISIBILITY_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {page_path}")
print(f"Created/updated: {test_path}")