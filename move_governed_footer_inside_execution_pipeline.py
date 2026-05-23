from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

backup = backup_dir / f"client_page_before_governed_footer_move_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

standalone_block = """
      <div
        style={{
          marginTop: 18,
          padding: "18px 22px",
          borderRadius: 20,
          background: "linear-gradient(90deg,#f5f3ff,#f8fafc)",
          border: "1px solid rgba(99,102,241,.10)",
          display: "flex",
          alignItems: "center",
          gap: 14,
        }}
      >
        <div
          style={{
            width: 34,
            height: 34,
            borderRadius: 999,
            background: "#ffffff",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#4f46e5",
            fontWeight: 900,
            boxShadow: "0 6px 16px rgba(15,23,42,.08)",
          }}
        >
          ✦
        </div>

        <div>
          <div
            style={{
              color: "#0f172a",
              fontWeight: 800,
              fontSize: 14,
              marginBottom: 2,
            }}
          >
            Governed execution, every time.
          </div>

          <div
            style={{
              color: "#64748b",
              fontSize: 13,
              lineHeight: 1.45,
            }}
          >
            All steps are tracked, logged, and optimised for quality and consistency.
          </div>
        </div>
      </div>
"""

if standalone_block not in text:
    raise SystemExit("Could not locate standalone governed footer block.")

text = text.replace(standalone_block, "", 1)

pipeline_marker = """
            ))}
          </div>
"""

replacement = """
            ))}
          </div>

          <div
            style={{
              marginTop: 16,
              padding: "18px 20px",
              borderRadius: 18,
              background: "linear-gradient(90deg,#f5f3ff,#f8fafc)",
              border: "1px solid rgba(99,102,241,.10)",
              display: "flex",
              alignItems: "center",
              gap: 14,
            }}
          >
            <div
              style={{
                width: 34,
                height: 34,
                borderRadius: 999,
                background: "#ffffff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#4f46e5",
                fontWeight: 900,
                boxShadow: "0 6px 16px rgba(15,23,42,.08)",
              }}
            >
              ✦
            </div>

            <div>
              <div
                style={{
                  color: "#0f172a",
                  fontWeight: 800,
                  fontSize: 14,
                  marginBottom: 2,
                }}
              >
                Governed execution, every time.
              </div>

              <div
                style={{
                  color: "#64748b",
                  fontSize: 13,
                  lineHeight: 1.45,
                }}
              >
                All steps are tracked, logged, and optimised for quality and consistency.
              </div>
            </div>
          </div>
"""

if pipeline_marker not in text:
    raise SystemExit("Could not locate execution pipeline marker.")

text = text.replace(pipeline_marker, replacement, 1)

path.write_text(text, encoding="utf-8")

print("GOVERNED_EXECUTION_FOOTER_MOVED_INSIDE_PIPELINE")
print(f"Backup: {backup}")