from pathlib import Path
from datetime import datetime
import re

ROOT = Path.cwd()
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"client_page_before_ux_pass8_compact_workspace_pills_{timestamp}.tsx"

text = PAGE.read_text(encoding="utf-8")
original = text
backup.write_text(original, encoding="utf-8")

# 1) Replace the bulky Connections card section with compact integration pills.
start_marker = '''        <section style={cardStyle}>
          <StepHeader number="00" title="Connections" />'''
end_marker = '''        <section style={responsiveWorkspaceGridStyle}>'''

start = text.find(start_marker)
end = text.find(end_marker, start)

if start == -1 or end == -1:
    raise RuntimeError("Could not locate Connections section for replacement.")

integration_pills_section = r'''        <section
          style={{
            ...cardStyle,
            padding: 18,
            marginBottom: 18,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: 16,
              flexWrap: "wrap",
            }}
          >
            <div>
              <div style={{ fontSize: 13, fontWeight: 800, color: "#0f172a" }}>Integrations</div>
              <div style={{ color: "#64748b", fontSize: 12, marginTop: 2 }}>Connected systems</div>
            </div>

            <div
              style={{
                display: "flex",
                gap: 10,
                flexWrap: "wrap",
                alignItems: "center",
                flex: 1,
              }}
            >
              {(integrations.length ? integrations : DEFAULT_CLIENT_INTEGRATIONS).slice(0, 6).map((integration) => (
                <button
                  key={integration.integration_key}
                  type="button"
                  onClick={() => integration.connected ? testIntegration(integration) : connectIntegration(integration)}
                  style={{
                    border: "1px solid rgba(15, 23, 42, 0.10)",
                    background: "#ffffff",
                    borderRadius: 14,
                    padding: "9px 12px",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 9,
                    cursor: "pointer",
                    boxShadow: "0 5px 18px rgba(15,23,42,0.035)",
                    minWidth: 148,
                  }}
                >
                  <span
                    style={{
                      width: 28,
                      height: 28,
                      borderRadius: 10,
                      display: "inline-flex",
                      alignItems: "center",
                      justifyContent: "center",
                      background: integration.connected ? "#ecfdf5" : "#f1f5f9",
                      color: integration.connected ? "#16a34a" : "#64748b",
                      fontWeight: 900,
                      fontSize: 12,
                    }}
                  >
                    {integration.name.slice(0, 1)}
                  </span>
                  <span style={{ display: "grid", lineHeight: 1.1, textAlign: "left" }}>
                    <span style={{ fontWeight: 800, color: "#0f172a", fontSize: 12 }}>{integration.name}</span>
                    <span style={{ color: integration.connected ? "#16a34a" : "#64748b", fontSize: 11, fontWeight: 700 }}>
                      {integration.connected ? "Connected" : "Connect"}
                    </span>
                  </span>
                </button>
              ))}

              <button
                type="button"
                style={{
                  border: "1px solid rgba(37, 99, 235, 0.16)",
                  background: "linear-gradient(135deg,#eff6ff,#ffffff)",
                  color: "#2563eb",
                  borderRadius: 14,
                  padding: "10px 13px",
                  fontWeight: 800,
                  cursor: "pointer",
                }}
              >
                + Add integration
              </button>
            </div>
          </div>
        </section>


'''

text = text[:start] + integration_pills_section + text[end:]

# 2) Make Run Agent block more compact.
text = text.replace(
    'gridTemplateColumns: "280px minmax(0,1fr)"',
    'gridTemplateColumns: "245px minmax(0,1fr)"'
)

text = text.replace(
    'gap: 18, marginTop: 18',
    'gap: 14, marginTop: 14'
)

text = text.replace(
    'padding: "9px 11px"',
    'padding: "7px 9px"'
)

text = text.replace(
    'fontSize: 12.5,',
    'fontSize: 12,'
)

text = text.replace(
    'display: "grid", gap: 10',
    'display: "grid", gap: 7'
)

text = text.replace(
    'rows={5}',
    'rows={4}'
)

# 3) Remove excessive vertical min heights inserted into controls.
text = re.sub(
    r'\n\s*minHeight:\s*120,',
    '',
    text,
)

text = re.sub(
    r'\n\s*minHeight:\s*"100%",',
    '',
    text,
)

# 4) Fix elongated execution pipeline number bubbles.
text = text.replace(
    '''width: 28,
                      height: 28,
                      borderRadius: 16,''',
    '''width: 30,
                      height: 30,
                      minWidth: 30,
                      minHeight: 30,
                      borderRadius: 999,'''
)

text = text.replace(
    '''width: 28,
                height: 28,
                borderRadius: 16,''',
    '''width: 30,
                height: 30,
                minWidth: 30,
                minHeight: 30,
                borderRadius: 999,'''
)

# 5) Reduce title and top spacing slightly in Run Agent section.
text = text.replace(
    'Select approved agents and launch governed execution.',
    'Select agents and launch governed execution.'
)

# 6) Marker.
if "client_portal_ux_pass8_compact_workspace_pills" not in text:
    text = text.replace(
        "// client_portal_ux_pass7_compact_agents_integrations",
        "// client_portal_ux_pass7_compact_agents_integrations\n// client_portal_ux_pass8_compact_workspace_pills"
    )

if text == original:
    raise RuntimeError("No Pass 8 changes applied.")

PAGE.write_text(text, encoding="utf-8")

TEST = ROOT / "test_client_portal_ux_pass8_compact_workspace_pills.py"
TEST.write_text(r'''
from pathlib import Path

PAGE = Path("frontend/src/app/client/page.tsx")
text = PAGE.read_text(encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS8_COMPACT_WORKSPACE_PILLS_RESULTS")

checks = {
    "marker": "client_portal_ux_pass8_compact_workspace_pills" in text,
    "integration_pills": "+ Add integration" in text and "Connected systems" in text,
    "compact_agent_grid": 'gridTemplateColumns: "245px minmax(0,1fr)"' in text,
    "task_rows": "rows={4}" in text,
    "bubble_fix": "minWidth: 30" in text and "borderRadius: 999" in text,
    "no_window_innerwidth": "window.innerWidth" not in text,
}

for key, value in checks.items():
    print(key, value)

assert all(checks.values())

print("CLIENT_PORTAL_UX_PASS8_COMPACT_WORKSPACE_PILLS_OK")
'''.lstrip(), encoding="utf-8")

print("CLIENT_PORTAL_UX_PASS8_COMPACT_WORKSPACE_PILLS_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")
print(f"Created: {TEST}")