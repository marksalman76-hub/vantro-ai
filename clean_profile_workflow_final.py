from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

backup = backup_dir / f"client_page_before_clean_profile_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

old_tabs = '''            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 14 }}>
              {[
                ["settings", "⚙️ Settings"],
                ["profile", "👤 Profile"],
                ["password-reset", "🔐 Password reset"],
                ["two-factor-authentication", "🛡️ 2FA"],
              ].map(([key, label]) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => {
                    setActiveAccountPanel(key);
                    window.location.hash = key;
                  }}
                  style={{
                    border: activeAccountPanel === key ? "1px solid rgba(79,70,229,.35)" : "1px solid #e5eaf2",
                    background: activeAccountPanel === key ? "rgba(238,242,255,.95)" : "#fff",
                    color: activeAccountPanel === key ? "#4f46e5" : "#334155",
                    borderRadius: 999,
                    padding: "9px 12px",
                    fontWeight: 850,
                    cursor: "pointer",
                    fontSize: 12,
                  }}
                >
                  {label}
                </button>
              ))}
            </div>
'''

text = text.replace(old_tabs, "")

old_profile = '''              {activeAccountPanel === "profile" ? (
                <>
                  <div style={{ border: "1px solid #edf1f6", borderRadius: 16, padding: 14, background: "#fff" }}>
                    <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>Client</div>
                    <div style={{ marginTop: 6, color: "var(--color-dark)", fontWeight: 900 }}>{clientDisplayName}</div>
                    <div style={{ marginTop: 5, color: "var(--color-muted)", fontSize: 12 }}>{clientEmail || "No email shown"}</div>
                  </div>
                  <div style={{ border: "1px solid #edf1f6", borderRadius: 16, padding: 14, background: "#fff" }}>
                    <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>Business profile</div>
                    <div style={{ marginTop: 6, color: "var(--color-dark)", fontWeight: 900 }}>{businessProfile.business_name || "Not saved yet"}</div>
                    <div style={{ marginTop: 5, color: "var(--color-muted)", fontSize: 12 }}>Edit the Business Profile Intelligence section below.</div>
                  </div>
                </>
              ) : null}
'''

new_profile = '''              {activeAccountPanel === "profile" ? (
                <>
                  <div style={{ border: "1px solid #edf1f6", borderRadius: 16, padding: 14, background: "#fff" }}>
                    <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>Client</div>

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
                        marginTop: 8,
                        width: "100%",
                        height: 42,
                        border: "1.5px solid rgba(79,70,229,.35)",
                        borderRadius: 10,
                        padding: "9px 11px",
                        fontSize: 13,
                        color: "#0f172a",
                        background: "#fff",
                        outline: "none",
                        boxSizing: "border-box",
                        fontFamily: "inherit",
                      }}
                    />

                    <div style={{ marginTop: 8, color: "var(--color-muted)", fontSize: 12 }}>
                      {clientEmail || "No email shown"}
                    </div>
                  </div>

                  <div style={{ border: "1px solid #edf1f6", borderRadius: 16, padding: 14, background: "#fff" }}>
                    <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>
                      Business profile
                    </div>

                    <div style={{ marginTop: 6, color: "var(--color-dark)", fontWeight: 900 }}>
                      {businessProfile.business_name || "Not saved yet"}
                    </div>

                    <div style={{ marginTop: 5, color: "var(--color-muted)", fontSize: 12 }}>
                      Edit the Business Profile Intelligence section below.
                    </div>
                  </div>
                </>
              ) : null}
'''

if old_profile not in text:
    raise SystemExit("Could not locate profile section safely.")

text = text.replace(old_profile, new_profile)

path.write_text(text, encoding="utf-8")

print("PROFILE_WORKFLOW_FIXED")
print(f"Backup: {backup}")