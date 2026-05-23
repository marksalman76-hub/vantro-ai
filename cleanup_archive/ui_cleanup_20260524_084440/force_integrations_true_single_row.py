from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_true_single_row_integrations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

start = text.find('<h2 style={{ margin: 0 }}>Integrations</h2>')
if start == -1:
    raise SystemExit("Could not find Integrations heading.")

section_start = text.rfind("<section", 0, start)
section_end = text.find("</section>", start)

if section_start == -1 or section_end == -1:
    raise SystemExit("Could not find Integrations section.")

section_end += len("</section>")
old = text[section_start:section_end]

new = r'''<section
        style={{
          ...cardStyle,
          padding: "16px 22px",
          marginBottom: 18,
          display: "grid",
          gridTemplateColumns: "145px repeat(6, minmax(118px, 1fr)) 150px",
          gap: 12,
          alignItems: "center",
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
              padding: "9px 10px",
              display: "flex",
              alignItems: "center",
              gap: 9,
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
            <span style={{ minWidth: 0, textAlign: "left" }}>
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
              <span style={{ display: "block", color: "var(--color-muted)", fontSize: 12, fontWeight: 800 }}>
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
            padding: "10px 12px",
            fontWeight: 900,
            cursor: "pointer",
            whiteSpace: "nowrap",
          }}
        >
          + Add integration
        </button>
      </section>'''

text = text[:section_start] + new + text[section_end:]

path.write_text(text, encoding="utf-8")

print("INTEGRATIONS_TRUE_SINGLE_ROW_FIXED")
print(f"Backup: {backup}")