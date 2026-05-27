from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step269_final_polish_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

# Tighten global page width/padding
text = text.replace('padding: "42px 22px"', 'padding: "34px 22px"')
text = text.replace('<section style={{ maxWidth: 1280, margin: "0 auto" }}>', '<section style={{ maxWidth: 1180, margin: "0 auto" }}>')

# Refine card glass style
text = text.replace(
'''const cardStyle = {
  background: "rgba(15,23,42,.75)",
  border: "1px solid rgba(148,163,184,.18)",
  borderRadius: 22,
};''',
'''const cardStyle = {
  background: "rgba(15,23,42,.66)",
  border: "1px solid rgba(148,163,184,.16)",
  borderRadius: 24,
  boxShadow: "0 20px 60px rgba(0,0,0,.22)",
  backdropFilter: "blur(14px)",
};'''
)

# Refine input style
text = text.replace(
'''const inputStyle = {
  width: "100%",
  padding: 13,
  borderRadius: 14,
  border: "1px solid rgba(148,163,184,.18)",
  background: "#020617",
  color: "#fff",
  resize: "vertical" as const,
  fontSize: 13,
};''',
'''const inputStyle = {
  width: "100%",
  padding: 12,
  borderRadius: 15,
  border: "1px solid rgba(148,163,184,.14)",
  background: "rgba(2,6,23,.72)",
  color: "#fff",
  resize: "vertical" as const,
  fontSize: 13,
  lineHeight: 1.45,
  outline: "none",
};'''
)

# Reduce hero title size slightly
text = text.replace('fontSize: 52, marginTop: 10', 'fontSize: 48, marginTop: 10')

# Compact summary cards
text = text.replace('].map(([label, value]) => (\n            <div key={label} style={{ ...cardStyle, padding: 22 }}>', '].map(([label, value]) => (\n            <div key={label} style={{ ...cardStyle, padding: 20 }}>')

# Compact business profile card
text = text.replace('<div style={{ ...cardStyle, padding: 22, marginTop: 24 }}>', '<div style={{ ...cardStyle, padding: 22, marginTop: 22 }}>')
text = text.replace('fontSize: 24, marginTop: 7', 'fontSize: 23, marginTop: 6')
text = text.replace('gap: 12,\n            }}\n          >\n            {businessFields.map', 'gap: 11,\n            }}\n          >\n            {businessFields.map')
text = text.replace('minHeight: 62,', 'minHeight: 56,')
text = text.replace('rows={2}', 'rows={2}')

# Improve execution grid spacing
text = text.replace('gridTemplateColumns: "minmax(360px,420px) 1fr"', 'gridTemplateColumns: "minmax(350px,410px) 1fr"')
text = text.replace('marginTop: 24,\n            alignItems: "start"', 'marginTop: 22,\n            alignItems: "start"')

# Improve agent selector height and task height
text = text.replace('maxHeight: 260,', 'maxHeight: 240,')
text = text.replace('rows={8}', 'rows={7}')

# Improve output viewer empty state text block
text = text.replace(
'''              <div
                style={{
                  marginTop: 20,
                  minHeight: 260,
                  borderRadius: 18,
                  border: "1px dashed rgba(148,163,184,.22)",
                  background: "rgba(2,6,23,.45)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  textAlign: "center",
                  padding: 28,
                  color: "#94a3b8",
                  lineHeight: 1.7,
                }}
              >
                Select one or more active agents, add the task, then run execution.
                Premium deliverables, approvals, billing blocks, and workflow
                results will appear here.
              </div>''',
'''              <div
                style={{
                  marginTop: 20,
                  minHeight: 300,
                  borderRadius: 20,
                  border: "1px dashed rgba(148,163,184,.20)",
                  background: "linear-gradient(135deg,rgba(2,6,23,.55),rgba(15,23,42,.35))",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  textAlign: "center",
                  padding: 34,
                  color: "#94a3b8",
                  lineHeight: 1.7,
                }}
              >
                <div>
                  <div style={{ color: "#e2e8f0", fontSize: 20, fontWeight: 800, marginBottom: 8 }}>
                    Ready for premium execution
                  </div>
                  <div>
                    Select active agents, add the task, then run execution.
                    Deliverables, approvals, billing blocks, and workflow results will appear here.
                  </div>
                </div>
              </div>'''
)

PAGE.write_text(text, encoding="utf-8")

print("STEP_269_FINAL_WORKSPACE_POLISH_INSTALLED")
print(f"Backup: {backup}")
print("STEP_269_OK")