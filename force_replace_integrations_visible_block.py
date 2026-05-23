from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_force_replace_integrations_visible_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

marker = "Connected systems"
button_marker = "+ Add integration"

marker_index = text.find(marker)
button_index = text.find(button_marker, marker_index)

if marker_index == -1 or button_index == -1:
    raise SystemExit("Could not find visible integrations block markers.")

section_start = text.rfind("<section", 0, marker_index)
section_end = text.find("</section>", button_index)

if section_start == -1 or section_end == -1:
    raise SystemExit("Could not locate integrations section boundaries.")

section_end += len("</section>")

replacement = r'''<section
        style={{
          ...cardStyle,
          padding: "14px 18px",
          marginBottom: 18,
        }}
      >
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "150px repeat(6, minmax(130px, 1fr)) 155px",
            gap: 10,
            alignItems: "center",
            width: "100%",
          }}
        >
          <div>
            <h2 style={{ margin: 0, fontSize: 16 }}>Integrations</h2>
            <p style={{ margin: "4px 0 0", color: "var(--color-muted)", fontSize: 13 }}>
              Connected systems
            </p>
          </div>

          {[
            ["E", "Email"],
            ["C", "CRM"],
            ["E", "Ecommerce Store"],
            ["W", "Website / CMS"],
            ["C", "Calendar"],
            ["S", "SMS / Phone"],
          ].map(([letter, label]) => (
            <button
              key={label}
              type="button"
              style={{
                border: "1px solid #e5eaf2",
                borderRadius: 12,
                background: "#fff",
                padding: "8px 10px",
                display: "flex",
                alignItems: "center",
                gap: 8,
                minHeight: 48,
                cursor: "pointer",
                boxShadow: "0 8px 20px rgba(15,23,42,.04)",
                whiteSpace: "nowrap",
                overflow: "hidden",
              }}
            >
              <span
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: 9,
                  background: "#eef2f7",
                  color: "#64748b",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: 900,
                  flex: "0 0 auto",
                }}
              >
                {letter}
              </span>
              <span style={{ minWidth: 0, textAlign: "left", lineHeight: 1.1 }}>
                <span
                  style={{
                    display: "block",
                    fontWeight: 900,
                    color: "var(--color-dark)",
                    fontSize: 13,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                  }}
                >
                  {label}
                </span>
                <span style={{ display: "block", color: "var(--color-muted)", fontSize: 12, fontWeight: 800, marginTop: 3 }}>
                  Connect
                </span>
              </span>
            </button>
          ))}

          <button
            type="button"
            style={{
              border: "1px solid #d8dcff",
              borderRadius: 12,
              background: "#fff",
              color: "var(--color-primary)",
              padding: "8px 12px",
              minHeight: 48,
              fontWeight: 900,
              cursor: "pointer",
              whiteSpace: "nowrap",
            }}
          >
            + Add integration
          </button>
        </div>
      </section>'''

text = text[:section_start] + replacement + text[section_end:]
path.write_text(text, encoding="utf-8")

print("VISIBLE_INTEGRATIONS_BLOCK_FORCE_REPLACED")
print(f"Backup: {backup}")