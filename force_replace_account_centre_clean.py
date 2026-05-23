from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_force_account_centre_clean_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

start = text.find("        {activeAccountPanel ? (")
end = text.find("        <section style={{ ...cardStyle, padding: 18, marginBottom: 18", start)

if start == -1 or end == -1 or end <= start:
    raise SystemExit("Could not locate Account Centre block safely.")

clean_block = r'''        {activeAccountPanel ? (
          <section style={{ ...cardStyle, padding: 18, marginBottom: 18 }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 14, alignItems: "flex-start", flexWrap: "wrap" }}>
              <div>
                <div style={{ color: "var(--color-brand)", fontSize: 12, fontWeight: 900, letterSpacing: .6, textTransform: "uppercase", marginBottom: 6 }}>
                  Account centre
                </div>
                <h2 style={{ margin: 0, color: "var(--color-dark)", fontSize: 22, letterSpacing: -.4 }}>
                  Profile
                </h2>
                <p style={{ margin: "7px 0 0", color: "var(--color-muted)", fontSize: 13, lineHeight: 1.45 }}>
                  Manage client account controls without leaving the workspace.
                </p>
              </div>

              <button
                type="button"
                onClick={() => {
                  setActiveAccountPanel("");
                  window.location.hash = "";
                }}
                style={{ border: "1px solid #e5eaf2", background: "#fff", borderRadius: 999, padding: "9px 13px", fontWeight: 850, cursor: "pointer", color: "var(--color-dark)" }}
              >
                Close
              </button>
            </div>

            <div style={{ marginTop: 14, display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(260px,1fr))", gap: 12 }}>
              <div style={{ border: "1px solid #edf1f6", borderRadius: 16, padding: 14, background: "#fff" }}>
                <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>Client</div>
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
                    height: 40,
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
          </section>
        ) : null}

'''

text = text[:start] + clean_block + text[end:]

bad_terms = ["⚙️ Settings", "👤 Profile", "🔐 Password reset", "🛡️ 2FA"]
still_found = [term for term in bad_terms if term in text]
if still_found:
    raise SystemExit(f"Unwanted account buttons still found: {still_found}")

if 'aria-label="Client name"' not in text:
    raise SystemExit("Editable client input was not installed.")

path.write_text(text, encoding="utf-8")

print("FORCE_ACCOUNT_CENTRE_CLEAN_FIXED")
print(f"Backup: {backup}")