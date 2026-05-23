from pathlib import Path
from datetime import datetime
import re

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_clean_account_centre_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

# Remove the unnecessary Settings/Profile/Password/2FA button row.
text = re.sub(
    r'\n\s*<div style=\{\{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 14 \}\}>[\s\S]*?</div>\s*\n\s*<div style=\{\{ marginTop: 14, display: "grid"',
    '\n\n            <div style={{ marginTop: 14, display: "grid"',
    text,
    count=1,
)

# Replace the account-centre profile card grid with editable client name + business profile card.
old_start = text.find('            <div style={{ marginTop: 14, display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 12 }}>')
old_end = text.find('          </section>\n        ) : null}', old_start)

if old_start == -1 or old_end == -1:
    raise SystemExit("Could not find account centre card area.")

new_block = r'''            <div style={{ marginTop: 14, display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 12 }}>
              <div style={{ border: "1px solid #edf1f6", borderRadius: 16, padding: 14, background: "#fff" }}>
                <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>Client</div>
                <div style={{ marginTop: 6, color: "var(--color-dark)", fontWeight: 900 }}>Client</div>
                <input
                  type="text"
                  aria-label="Client name"
                  placeholder="Type client name here"
                  value={businessProfile.client_name || ""}
                  onChange={(e) => {
                    setBusinessProfile((prev) => ({ ...prev, client_name: e.target.value }));
                    setBusinessProfileSaved(false);
                  }}
                  style={{
                    marginTop: 8,
                    width: "100%",
                    height: 38,
                    border: "1.5px solid rgba(79,70,229,.35)",
                    borderRadius: 10,
                    padding: "8px 10px",
                    fontSize: 13,
                    fontFamily: "inherit",
                    color: "#0f172a",
                    outline: "none",
                    boxSizing: "border-box",
                    cursor: "text",
                    background: "#fff",
                  }}
                />
                <div style={{ marginTop: 8, color: "var(--color-muted)", fontSize: 12 }}>{clientEmail || "No email shown"}</div>
              </div>

              <div style={{ border: "1px solid #edf1f6", borderRadius: 16, padding: 14, background: "#fff" }}>
                <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>Business profile</div>
                <div style={{ marginTop: 6, color: "var(--color-dark)", fontWeight: 900 }}>{businessProfileSaved ? "Saved" : "Not saved yet"}</div>
                <div style={{ marginTop: 5, color: "var(--color-muted)", fontSize: 12 }}>Edit the Business Profile Intelligence section below.</div>
              </div>
            </div>
'''

text = text[:old_start] + new_block + text[old_end:]

path.write_text(text, encoding="utf-8")
print("ACCOUNT_CENTRE_CLEAN_EDITABLE_CLIENT_FIXED")
print(f"Backup: {backup}")