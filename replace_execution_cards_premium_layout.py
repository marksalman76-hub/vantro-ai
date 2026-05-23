from pathlib import Path
from datetime import datetime
import re

path = Path("frontend/src/app/client/page.tsx")
text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"client_page_before_premium_execution_cards_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

start_marker = "RUN AI AGENT"
end_marker = "EXECUTION WORKSPACE"

start = text.find(start_marker)
end = text.find(end_marker, start)

if start == -1 or end == -1:
    raise SystemExit("Could not locate execution cards block.")

block_start = text.rfind("<div", 0, start)
block_end = text.rfind("<section", 0, end)

if block_start == -1 or block_end == -1:
    raise SystemExit("Could not locate safe replacement boundaries.")

new_block = r'''<div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 18,
          alignItems: "stretch",
          marginBottom: 18,
        }}
      >
        <section style={{ ...cardStyle, padding: 24, borderRadius: 28 }}>
          <StepHeader number="01" title="Run AI Agent" />
          <h2 style={{ ...cardTitle, marginBottom: 20 }}>
            Select agents and launch governed execution.
          </h2>

          <div style={{ marginBottom: 18 }}>
            <div style={labelStyle}>Active agents</div>

            <div
              style={{
                display: "flex",
                gap: 10,
                overflowX: "auto",
                padding: "4px 4px 12px",
                scrollbarWidth: "thin",
              }}
            >
              {selectedAgents.slice(0, 12).map((agent, index) => (
                <button
                  key={agent}
                  type="button"
                  onClick={() => toggleAgent(agent)}
                  style={{
                    flex: "0 0 180px",
                    minHeight: 78,
                    border: "1px solid rgba(79,70,229,.16)",
                    borderRadius: 16,
                    background: "linear-gradient(180deg,#ffffff 0%,#f7f7ff 100%)",
                    boxShadow: "0 12px 28px rgba(15,23,42,.06)",
                    padding: "12px 12px",
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                    textAlign: "left",
                    position: "relative",
                  }}
                >
                  <span
                    style={{
                      width: 34,
                      height: 34,
                      borderRadius: 999,
                      background: "linear-gradient(135deg,#4f46e5,#06b6d4)",
                      color: "#fff",
                      display: "inline-flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontWeight: 900,
                      flex: "0 0 auto",
                    }}
                  >
                    {["👤", "🎯", "📈", "📅", "📣", "✍️", "🔍", "✉️"][index % 8]}
                  </span>

                  <span
                    style={{
                      color: "#0f172a",
                      fontSize: 12,
                      fontWeight: 900,
                      lineHeight: 1.25,
                    }}
                  >
                    {agent.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                  </span>

                  <span
                    style={{
                      position: "absolute",
                      top: 9,
                      right: 10,
                      color: "#22c55e",
                      fontSize: 13,
                    }}
                  >
                    ●
                  </span>
                </button>
              ))}
            </div>
          </div>

          <div style={{ marginBottom: 16 }}>
            <div style={labelStyle}>Task</div>
            <textarea
              value={task}
              onChange={(event) => setTask(event.target.value)}
              style={{
                width: "100%",
                minHeight: 128,
                borderRadius: 18,
                border: "1px solid #dbe3f0",
                padding: 16,
                boxSizing: "border-box",
                fontSize: 14,
                lineHeight: 1.45,
                outline: "none",
                resize: "vertical",
                fontFamily: "inherit",
                color: "#0f172a",
                background: "#fff",
              }}
            />
          </div>

          <button
            onClick={runSelectedAgents}
            style={{
              width: "100%",
              height: 56,
              border: "none",
              borderRadius: 18,
              color: "#fff",
              fontWeight: 900,
              fontSize: 15,
              cursor: "pointer",
              background: "linear-gradient(135deg,#4f46e5,#06b6d4)",
              boxShadow: "0 18px 36px rgba(6,182,212,.18)",
            }}
          >
            ✨ Run Agent
          </button>

          <p style={{ ...mutedText, marginTop: 18 }}>ⓘ Runs use your saved business profile.</p>
        </section>

        <section style={{ ...cardStyle, padding: 24, borderRadius: 28 }}>
          <StepHeader number="02" title="Live Execution Flow" />
          <h2 style={{ ...cardTitle, marginBottom: 8 }}>Execution pipeline</h2>
          <p style={{ ...mutedText, fontSize: 13.5, marginBottom: 20 }}>
            Every AI deliverable flows through approval, optimisation, workflow validation, and governed execution before deployment.
          </p>

          <div style={{ display: "grid", gap: 10 }}>
            {[
              ["1", "🚀", "Execution requested", "Started", "Live"],
              ["2", "📋", "Deliverable status", "Ready", "Live"],
              ["3", "👥", "Client review", "Pending", "Open"],
              ["4", "🛫", "Execution ready", "Next", "—"],
            ].map(([number, icon, title, subtitle, status]) => (
              <div
                key={title}
                style={{
                  display: "grid",
                  gridTemplateColumns: "42px 1fr auto",
                  alignItems: "center",
                  gap: 12,
                  border: "1px solid #e5eaf2",
                  borderRadius: 18,
                  padding: "12px 14px",
                  background: "#fff",
                  boxShadow: "0 10px 24px rgba(15,23,42,.04)",
                }}
              >
                <span
                  style={{
                    width: 36,
                    height: 36,
                    borderRadius: 999,
                    background: number === "4" ? "#06b6d4" : "#4f46e5",
                    color: "#fff",
                    display: "inline-flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontWeight: 900,
                  }}
                >
                  {number}
                </span>

                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <span
                    style={{
                      width: 38,
                      height: 38,
                      borderRadius: 14,
                      background: "#f4f1ff",
                      display: "inline-flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    {icon}
                  </span>
                  <span>
                    <strong style={{ display: "block", color: "#0f172a", fontSize: 13.5 }}>
                      {title}
                    </strong>
                    <span style={{ color: "#64748b", fontSize: 12.5 }}>{subtitle}</span>
                  </span>
                </div>

                <span
                  style={{
                    border: status === "—" ? "1px solid #e5eaf2" : "1px solid #bbf7d0",
                    background: status === "—" ? "#f8fafc" : "#f0fdf4",
                    color: status === "—" ? "#64748b" : "#16a34a",
                    borderRadius: 999,
                    padding: "6px 10px",
                    fontSize: 12,
                    fontWeight: 850,
                    whiteSpace: "nowrap",
                  }}
                >
                  {status}
                </span>
              </div>
            ))}
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 14,
              marginTop: 22,
              padding: 18,
              borderRadius: 18,
              background: "linear-gradient(90deg,#f4f1ff,#f8fafc)",
              border: "1px solid rgba(79,70,229,.08)",
            }}
          >
            <div
              style={{
                width: 42,
                height: 42,
                borderRadius: 16,
                background: "linear-gradient(135deg,#ede9fe,#f5f3ff)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 900,
                color: "#4f46e5",
              }}
            >
              ✦
            </div>
            <div>
              <div style={{ fontWeight: 900, color: "#0f172a", fontSize: 14 }}>
                Governed execution, every time.
              </div>
              <div style={{ color: "#64748b", fontSize: 13, marginTop: 3 }}>
                All steps are tracked, logged, and optimised for quality and consistency.
              </div>
            </div>
          </div>
        </section>
      </div>

      '''

text = text[:block_start] + new_block + text[block_end:]

path.write_text(text, encoding="utf-8")

print("PREMIUM_EXECUTION_CARDS_REPLACED")
print(f"Backup: {backup}")