from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()

target = root / "frontend" / "src" / "app" / "client" / "page.tsx"

if not target.exists():
    raise SystemExit(f"Missing file: {target}")

backup_dir = root / "backups" / f"inject_live_row3_lock_notice_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)

shutil.copy2(target, backup_dir / "page.tsx")

text = target.read_text(encoding="utf-8")

anchor = '{activeAccountPanel === "profile-edit" ? ('

if anchor not in text:
    raise SystemExit("profile-edit render block not found.")

notice_block = """
{activeAccountPanel === "profile-edit" ? (
  <>
    <div
      style={{
        marginBottom: 14,
        border: darkModeEnabled
          ? "1px solid rgba(251,191,36,.34)"
          : "1px solid #fde68a",
        borderRadius: 16,
        padding: 14,
        background: darkModeEnabled
          ? "rgba(120,53,15,.20)"
          : "#fff7ed",
        boxShadow: darkModeEnabled
          ? "0 12px 32px rgba(0,0,0,.20)"
          : "none",
      }}
    >
      <div
        style={{
          fontSize: 13,
          fontWeight: 900,
          color: darkModeEnabled ? "#fde68a" : "#92400e",
        }}
      >
        Agent selections are locked after activation
      </div>

      <div
        style={{
          marginTop: 6,
          fontSize: 12,
          lineHeight: 1.5,
          color: darkModeEnabled ? "#fcd34d" : "#78350f",
        }}
      >
        Package changes, swaps, upgrades, or added agents require owner/admin approval.
      </div>
    </div>
"""

updated = text.replace(
    anchor,
    notice_block + "\n" + anchor,
    1,
)

target.write_text(updated, encoding="utf-8")

print("LIVE_ROW3_LOCK_NOTICE_INJECTED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")