from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_compact_profile_panel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

start = text.find('{activeAccountPanel === "profile" ? (')
end = text.find('{activeAccountPanel === "password-reset" ? (', start)

if start == -1 or end == -1 or end <= start:
    raise SystemExit("Could not find profile panel block safely.")

new_profile_block = r'''{activeAccountPanel === "profile" ? (
                <div
                  style={{
                    gridColumn: "1 / -1",
                    display: "grid",
                    gridTemplateColumns: "minmax(260px, 1fr) minmax(260px, 1fr) auto",
                    gap: 16,
                    alignItems: "center",
                    border: "1px solid #edf1f6",
                    borderRadius: 16,
                    padding: "14px 16px",
                    background: "#fff",
                    minHeight: 96,
                  }}
                >
                  <div>
                    <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 900, textTransform: "uppercase", marginBottom: 7 }}>
                      Client
                    </div>
                    <input
                      type="text"
                      value={businessProfile.business_name || ""}
                      onChange={(e) => {
                        setBusinessProfile((prev) => ({
                          ...prev,
                          business_name: e.target.value,
                        }));
                        setBusinessProfileSaved(false);
                      }}
                      placeholder="Type business name here"
                      style={{
                        width: "100%",
                        height: 38,
                        border: "1.5px solid rgba(79,70,229,.35)",
                        borderRadius: 10,
                        padding: "8px 10px",
                        fontSize: 13,
                        color: "#0f172a",
                        background: "#fff",
                        outline: "none",
                        boxSizing: "border-box",
                        fontFamily: "inherit",
                      }}
                    />
                    <div style={{ marginTop: 6, color: "var(--color-muted)", fontSize: 12 }}>
                      {clientEmail || "No email shown"}
                    </div>
                  </div>

                  <div style={{ borderLeft: "1px solid #edf1f6", paddingLeft: 16 }}>
                    <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 900, textTransform: "uppercase", marginBottom: 7 }}>
                      Business profile
                    </div>
                    <div style={{ color: "var(--color-dark)", fontWeight: 900 }}>
                      {businessProfile.business_name || "Not saved yet"}
                    </div>
                    <div style={{ marginTop: 5, color: "var(--color-muted)", fontSize: 12 }}>
                      Edit the Business Profile Intelligence section below.
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={saveBusinessProfile}
                    style={{
                      border: 0,
                      borderRadius: 12,
                      padding: "12px 18px",
                      minWidth: 150,
                      background: "linear-gradient(135deg,#4f46e5,#4338ca)",
                      color: "#fff",
                      fontSize: 13,
                      fontWeight: 900,
                      cursor: "pointer",
                      boxShadow: "0 10px 24px rgba(79,70,229,.18)",
                      whiteSpace: "nowrap",
                    }}
                  >
                    ▣ Save profile
                  </button>
                </div>
              ) : null}

              '''

text = text[:start] + new_profile_block + text[end:]

path.write_text(text, encoding="utf-8")

print("COMPACT_PROFILE_PANEL_SAVE_LAYOUT_INSTALLED")
print(f"Backup: {backup}")