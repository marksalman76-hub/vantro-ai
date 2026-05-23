from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

src = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_left_run_agent_polish_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(src, encoding="utf-8")

old = '''          <div style={{ ...cardStyle, minHeight: 430 }}>
            <StepHeader number="01" title="Run AI Agent" />
            <h3 style={cardTitle}>Select agents and launch governed execution.</h3>

            <div style={{ display: "grid", gridTemplateColumns: "245px minmax(0,1fr)", gap: 14, marginTop: 10 }}>
              <div>
                <div style={labelStyle}>Active agents</div>
                <div style={{ display: "grid", gap: 7, maxHeight: 250, overflowY: "auto", paddingRight: 4 }}>
                  {(account?.active_agents || DEFAULT_AGENTS).map((agent) => {
                    const active = selectedAgents.includes(agent);
                    return (
                      <button
                        key={getAgentDisplayName(agent)}
                        onClick={() => toggleAgent(agent)}
                        style={{
                          border: active ? "1px solid rgba(37, 99, 235, 0.38)" : "1px solid rgba(15, 23, 42, 0.10)",
                          background: active ? "linear-gradient(135deg,#eff6ff,#ffffff)" : "#ffffff",
                          color: active ? "var(--color-brand)" : "var(--color-dark)",
                          padding: "7px 9px",
                          borderRadius: 12,
                          cursor: "pointer",
                          textAlign: "left",
                          fontSize: 11.8,
                          fontWeight: 700,
                          transition: "all 0.18s ease",
                          boxShadow: active ? "0 10px 30px rgba(37,99,235,0.10)" : "0 1px 2px rgba(15,23,42,0.03)",
                        }}
                      >
                        {active ? "● " : "○ "}
                        {getAgentDisplayName(agent)}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div>
                <div style={labelStyle}>Task</div>
                <textarea
                  defaultValue="Create a client-specific client deliverable using the saved business profile, selected active agents, current offer, target audience, goals, and execution requirements."
                  style={{
                    width: "100%",
                    minHeight: 150,
                    resize: "none",
                    borderRadius: 16,
                    border: "1px solid #dbe3ee",
                    background: "#fff",
                    padding: 14,
                    fontSize: 11.8,
                    lineHeight: 1.42,
                    boxSizing: "border-box",
                    fontFamily: "inherit",
                  }}
                />

                <button'''

new = '''          <div style={{ ...cardStyle, minHeight: 430 }}>
            <StepHeader number="01" title="Run AI Agent" />
            <h3 style={cardTitle}>Select agents and launch governed execution.</h3>
            <p style={{ ...mutedText, margin: "6px 0 0" }}>
              Configure your task and run using your saved business profile.
            </p>

            <div style={{ display: "grid", gridTemplateColumns: "260px minmax(0,1fr)", gap: 16, marginTop: 18 }}>
              <div>
                <div style={labelStyle}>Active agents</div>
                <div style={{ display: "grid", gap: 7, maxHeight: 268, overflowY: "auto", paddingRight: 4 }}>
                  {(account?.active_agents || DEFAULT_AGENTS).map((agent) => {
                    const active = selectedAgents.includes(agent);
                    const agentName = getAgentDisplayName(agent);
                    const agentIcon =
                      agentName.toLowerCase().includes("research") ? "⌕" :
                      agentName.toLowerCase().includes("copy") ? "✎" :
                      agentName.toLowerCase().includes("ugc") ? "▣" :
                      agentName.toLowerCase().includes("image") ? "▧" :
                      agentName.toLowerCase().includes("crm") ? "♟" :
                      agentName.toLowerCase().includes("email") ? "✉" :
                      agentName.toLowerCase().includes("analytics") ? "↗" :
                      agentName.toLowerCase().includes("influencer") ? "★" :
                      "AI";

                    return (
                      <button
                        key={agentName}
                        onClick={() => toggleAgent(agent)}
                        style={{
                          border: active ? "1px solid rgba(37, 99, 235, 0.34)" : "1px solid rgba(15, 23, 42, 0.10)",
                          background: active ? "linear-gradient(135deg,#eff6ff,#ffffff)" : "#ffffff",
                          color: active ? "var(--color-brand)" : "var(--color-dark)",
                          padding: "8px 10px",
                          borderRadius: 13,
                          cursor: "pointer",
                          textAlign: "left",
                          fontSize: 11.8,
                          fontWeight: 760,
                          transition: "all 0.18s ease",
                          boxShadow: active ? "0 10px 30px rgba(37,99,235,0.10)" : "0 1px 2px rgba(15,23,42,0.03)",
                          display: "grid",
                          gridTemplateColumns: "18px 28px minmax(0,1fr)",
                          gap: 8,
                          alignItems: "center",
                        }}
                      >
                        <span
                          style={{
                            width: 14,
                            height: 14,
                            borderRadius: 999,
                            border: active ? "none" : "1.5px solid rgba(79,70,229,.45)",
                            background: active ? "var(--color-brand)" : "#ffffff",
                            color: "#fff",
                            display: "inline-flex",
                            alignItems: "center",
                            justifyContent: "center",
                            fontSize: 9,
                            fontWeight: 900,
                          }}
                        >
                          {active ? "✓" : ""}
                        </span>
                        <span
                          style={{
                            width: 26,
                            height: 26,
                            borderRadius: 9,
                            background: active ? "#eef2ff" : "#f8fafc",
                            color: "var(--color-brand)",
                            display: "inline-flex",
                            alignItems: "center",
                            justifyContent: "center",
                            fontSize: 13,
                            fontWeight: 900,
                          }}
                        >
                          {agentIcon}
                        </span>
                        <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                          {agentName}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>

              <div>
                <div style={labelStyle}>Task</div>
                <textarea
                  defaultValue="Create a client-specific client deliverable using the saved business profile, selected active agents, current offer, target audience, goals, and execution requirements."
                  style={{
                    width: "100%",
                    minHeight: 178,
                    resize: "none",
                    borderRadius: 16,
                    border: "1px solid #dbe3ee",
                    background: "#fff",
                    padding: 14,
                    fontSize: 11.8,
                    lineHeight: 1.46,
                    boxSizing: "border-box",
                    fontFamily: "inherit",
                  }}
                />

                <button'''

if old not in src:
    raise SystemExit("ERROR: Left Run AI Agent block not found. No changes made.")

src = src.replace(old, new, 1)

PAGE.write_text(src, encoding="utf-8")

print("LEFT_RUN_AGENT_SECTION_POLISHED_ONLY")
print(f"Backup: {backup}")
print("Right column untouched.")
print("Run AI Agent count:", src.count("Run AI Agent"))
print("Live execution flow count:", src.count("Live execution flow"))
print("Business profile applied count:", src.count("Business profile applied"))
print("Governed execution count:", src.count("Governed execution, every time."))
print("Old mutations:", src.count("applyHorizontalExecutionLayout") + src.count("applyPremiumExecutionSectionLayout"))
print("Left polish installed:", "Configure your task and run using your saved business profile." in src and "agentIcon" in src and "maxHeight: 268" in src)