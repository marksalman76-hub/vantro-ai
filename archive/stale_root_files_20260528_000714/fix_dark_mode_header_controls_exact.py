from pathlib import Path
from datetime import datetime

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "client" / "page.tsx"
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"client_page_before_dark_header_controls_exact_{timestamp}.tsx"

s = target.read_text(encoding="utf-8")
backup.write_text(s, encoding="utf-8")

old_active = '''            <div
              style={{
                background: "#fff",
                borderRadius: 16,
                padding: "8px 10px",
                border: "1px solid #e5eaf2",
                fontWeight: 800,
                boxShadow: "0 8px 22px rgba(15,23,42,.045)",
                textTransform: "uppercase",
              }}
            >
              <span
                style={{
                  color: accountStatus === "active" || accountStatus === "paid" || accountStatus === "trialing" ? "#22c55e" : "#ef4444",
                  marginRight: 8,
                }}
              >
                ●
              </span>
              {accountStatus === "active" || accountStatus === "paid" || accountStatus === "trialing" ? "ACTIVE" : "INACTIVE"}
            </div>'''

new_active = '''            <div
              style={{
                background: darkModeEnabled ? "rgba(3, 18, 42, 0.92)" : "#fff",
                borderRadius: 16,
                padding: "9px 14px",
                border: darkModeEnabled ? "1px solid rgba(34,197,94,.42)" : "1px solid #e5eaf2",
                fontWeight: 900,
                boxShadow: darkModeEnabled ? "0 0 0 1px rgba(34,197,94,.12), 0 12px 34px rgba(0,0,0,.24)" : "0 8px 22px rgba(15,23,42,.045)",
                textTransform: "uppercase",
                color: darkModeEnabled ? "#ecfdf5" : "var(--color-dark)",
                display: "inline-flex",
                alignItems: "center",
                minHeight: 34,
              }}
            >
              <span
                style={{
                  color: accountStatus === "active" || accountStatus === "paid" || accountStatus === "trialing" ? "#22c55e" : "#ef4444",
                  marginRight: 8,
                  textShadow: darkModeEnabled ? "0 0 16px rgba(34,197,94,.65)" : "none",
                }}
              >
                ●
              </span>
              <span style={{ color: accountStatus === "active" || accountStatus === "paid" || accountStatus === "trialing" ? "#22c55e" : "#ef4444" }}>
                {accountStatus === "active" || accountStatus === "paid" || accountStatus === "trialing" ? "ACTIVE" : "INACTIVE"}
              </span>
            </div>'''

old_notify = '''            <button
              aria-label="Notifications"
              style={{
                width: 34,
                height: 34,
                borderRadius: 16,
                border: "1px solid #e5eaf2",
                background: "#fff",
                boxShadow: "0 8px 22px rgba(15,23,42,.045)",
                cursor: "pointer",
                position: "relative",
              }}
            >
              🔔'''

new_notify = '''            <button
              aria-label="Notifications"
              style={{
                width: 38,
                height: 38,
                borderRadius: 999,
                border: darkModeEnabled ? "1px solid rgba(255,255,255,.16)" : "1px solid #e5eaf2",
                background: darkModeEnabled ? "rgba(255,255,255,.10)" : "#fff",
                color: darkModeEnabled ? "#fff" : "var(--color-dark)",
                boxShadow: darkModeEnabled ? "0 0 0 1px rgba(255,255,255,.06), 0 12px 34px rgba(0,0,0,.24)" : "0 8px 22px rgba(15,23,42,.045)",
                cursor: "pointer",
                position: "relative",
              }}
            >
              🔔'''

old_summary = '''              <summary
                style={{
                  width: 34,
                  height: 34,
                  borderRadius: 16,
                  background: "var(--color-dark)",
                  color: "#fff",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: 760,
                  cursor: "pointer",
                  listStyle: "none",
                }}
              >
                {clientInitials}
              </summary>'''

new_summary = '''              <summary
                style={{
                  width: 42,
                  height: 42,
                  borderRadius: 999,
                  background: darkModeEnabled ? "linear-gradient(135deg, #4f46e5, #7c3aed)" : "var(--color-dark)",
                  border: darkModeEnabled ? "1px solid rgba(255,255,255,.18)" : "none",
                  color: "#fff",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: 900,
                  cursor: "pointer",
                  listStyle: "none",
                  boxShadow: darkModeEnabled ? "0 0 0 5px rgba(99,102,241,.18), 0 0 26px rgba(99,102,241,.62)" : "0 8px 22px rgba(15,23,42,.14)",
                }}
              >
                {clientInitials}
              </summary>'''

old_new_execution = '''            <button
              style={{
                border: "none",
                borderRadius: 12,
                padding: "8px 10px",
                background: "var(--color-dark)",
                color: "#fff",
                fontWeight: 700,
                cursor: "pointer",
                boxShadow: "0 10px 24px rgba(15,23,42,.12)",
              }}
            >
              + New execution
            </button>'''

new_new_execution = '''            <button
              style={{
                border: darkModeEnabled ? "1px solid rgba(124,58,237,.45)" : "none",
                borderRadius: 12,
                padding: "9px 13px",
                background: darkModeEnabled ? "rgba(79,70,229,.16)" : "var(--color-dark)",
                color: "#fff",
                fontWeight: 850,
                cursor: "pointer",
                boxShadow: darkModeEnabled ? "0 0 0 1px rgba(124,58,237,.12), 0 12px 32px rgba(0,0,0,.22)" : "0 10px 24px rgba(15,23,42,.12)",
              }}
            >
              + New execution
            </button>'''

replacements = [
    (old_new_execution, new_new_execution, "New execution button"),
    (old_active, new_active, "ACTIVE pill"),
    (old_notify, new_notify, "notification button"),
    (old_summary, new_summary, "profile summary"),
]

changed = 0
for old, new, label in replacements:
    if old not in s:
        print(f"NOT_FOUND: {label}")
    else:
        s = s.replace(old, new, 1)
        print(f"REPLACED: {label}")
        changed += 1

if changed < 4:
    raise SystemExit(f"Only replaced {changed}/4 blocks. Stopping to avoid partial UI change.")

target.write_text(s, encoding="utf-8")

print("DARK_MODE_HEADER_CONTROLS_EXACT_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {target}")