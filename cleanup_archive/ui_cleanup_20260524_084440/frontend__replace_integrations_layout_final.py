from pathlib import Path
from datetime import datetime
import re

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

backup = backup_dir / f"client_page_before_integrations_layout_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

pattern = re.compile(
    r'<section\s+style=\{\{\s*\.\.\.cardStyle,\s*padding:\s*"18px 22px".*?Add integration\s*</button>\s*</section>',
    re.DOTALL
)

replacement = r'''<section
        style={{
          ...cardStyle,
          padding: "16px 18px",
          marginBottom: 18,
          overflowX: "auto",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            minWidth: 1380,
          }}
        >
          <div style={{ minWidth: 150 }}>
            <h2 style={{ margin: 0, fontSize: 16 }}>Integrations</h2>
            <p
              style={{
                margin: "4px 0 0",
                color: "var(--color-muted)",
                fontSize: 13,
              }}
            >
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
                padding: "10px 12px",
                display: "flex",
                alignItems: "center",
                gap: 10,
                minWidth: 190,
                height: 58,
                cursor: "pointer",
                boxShadow: "0 8px 20px rgba(15,23,42,.04)",
                flexShrink: 0,
              }}
            >
              <span
                style={{
                  width: 30,
                  height: 30,
                  borderRadius: 10,
                  background: "#eef2f7",
                  color: "#64748b",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: 900,
                  flexShrink: 0,
                }}
              >
                {letter}
              </span>

              <span style={{ textAlign: "left", lineHeight: 1.15 }}>
                <span
                  style={{
                    display: "block",
                    fontWeight: 900,
                    color: "var(--color-dark)",
                    fontSize: 13,
                    whiteSpace: "nowrap",
                  }}
                >
                  {label}
                </span>

                <span
                  style={{
                    display: "block",
                    color: "var(--color-muted)",
                    fontSize: 12,
                    fontWeight: 800,
                    marginTop: 3,
                  }}
                >
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
              padding: "0 18px",
              height: 58,
              fontWeight: 900,
              cursor: "pointer",
              whiteSpace: "nowrap",
              flexShrink: 0,
            }}
          >
            + Add integration
          </button>
        </div>
      </section>'''

if not pattern.search(text):
    raise SystemExit("Could not safely locate integrations section.")

text = pattern.sub(replacement, text, count=1)

path.write_text(text, encoding="utf-8")

print("FINAL_INTEGRATIONS_LAYOUT_REPLACED")
print(f"Backup: {backup}")