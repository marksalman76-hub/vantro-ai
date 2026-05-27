from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step268_premium_workspace_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

text = text.replace(
'''      const healthRes = await fetch(`${API_BASE}/health`, {
        cache: "no-store",
      });

      setHealth(healthRes.ok ? "Platform online" : "Platform unavailable");''',
'''      if (!API_BASE) {
        setHealth("Local workspace");
        return;
      }

      const healthRes = await fetch(`${API_BASE}/health`, {
        cache: "no-store",
      });

      setHealth(healthRes.ok ? "Platform online" : "Platform unavailable");'''
)

profile_marker = "BUSINESS PROFILE INTELLIGENCE"
profile_pos = text.find(profile_marker)
if profile_pos == -1:
    raise SystemExit("ERROR: Business Profile panel marker not found.")

profile_start = text.rfind('<div style={{ ...cardStyle', 0, profile_pos)
execution_grid_marker = 'gridTemplateColumns: "minmax(360px,420px) 1fr",'
execution_grid_pos = text.find(execution_grid_marker, profile_pos)
profile_end = text.rfind('<div', 0, execution_grid_pos)

if profile_start == -1 or execution_grid_pos == -1 or profile_end == -1 or profile_end <= profile_start:
    raise SystemExit("ERROR: Could not safely locate Business Profile card boundaries.")

compact_profile = '''        <div style={{ ...cardStyle, padding: 22, marginTop: 24 }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              gap: 18,
              flexWrap: "wrap",
              alignItems: "center",
              marginBottom: 16,
            }}
          >
            <div>
              <div
                style={{
                  color: "#38bdf8",
                  fontSize: 12,
                  fontWeight: 900,
                  letterSpacing: 1.2,
                }}
              >
                BUSINESS PROFILE INTELLIGENCE
              </div>

              <h2 style={{ fontSize: 24, marginTop: 7 }}>
                Store context for smarter agent outputs
              </h2>

              <p
                style={{
                  color: "#94a3b8",
                  maxWidth: 760,
                  lineHeight: 1.55,
                  marginTop: 7,
                  fontSize: 14,
                }}
              >
                Add this once so every active agent can tailor strategy, copy,
                creative, competitor analysis, and execution to the client.
              </p>
            </div>

            <div
              style={{
                borderRadius: 999,
                padding: "9px 13px",
                background: "rgba(56,189,248,.10)",
                border: "1px solid rgba(56,189,248,.22)",
                color: "#bae6fd",
                fontSize: 12,
                fontWeight: 800,
              }}
            >
              Applied to execution
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit,minmax(210px,1fr))",
              gap: 12,
            }}
          >
            {businessFields.map(([label, key, placeholder]) => (
              <label key={key}>
                <div style={{ color: "#94a3b8", fontSize: 11, marginBottom: 6 }}>
                  {label}
                </div>

                <textarea
                  value={businessProfile[key]}
                  onChange={(event) =>
                    setBusinessProfile({
                      ...businessProfile,
                      [key]: event.target.value,
                    })
                  }
                  rows={2}
                  placeholder={placeholder}
                  style={{
                    ...inputStyle,
                    minHeight: 62,
                    padding: 11,
                    borderRadius: 13,
                    fontSize: 12,
                  }}
                />
              </label>
            ))}
          </div>
        </div>

'''

text = text[:profile_start] + compact_profile + text[profile_end:]

text = text.replace(
'''              <div style={{ marginTop: 20, color: "#94a3b8", lineHeight: 1.7 }}>
                Generated outputs, billing blocks, approvals, premium deliverables,
                and workflow results will appear here after execution.
              </div>''',
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
              </div>'''
)

PAGE.write_text(text, encoding="utf-8")

print("STEP_268_PREMIUM_WORKSPACE_REFINEMENT_INSTALLED")
print(f"Backup: {backup}")
print("STEP_268_OK")