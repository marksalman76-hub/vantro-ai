from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
FILE = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"admin_page_before_deployment_agent_selector_{stamp}.tsx"
shutil.copy2(FILE, backup)

s = FILE.read_text(encoding="utf-8")

s = s.replace(
    'const [selectedAdminAgents, setSelectedAdminAgents] = useState<string[]>(["product_copywriting_agent"]);',
    '''const [selectedAdminAgents, setSelectedAdminAgents] = useState<string[]>(["product_copywriting_agent"]);
  const [selectedDeploymentAgents, setSelectedDeploymentAgents] = useState<string[]>(
    ADMIN_AGENT_OPTIONS.map(([agentId]) => agentId)
  );'''
)

insert_after = '''  function toggleAdminAgent(agentId: string) {
    setSelectedAdminAgents((current) => {
      if (current.includes(agentId)) {
        return current.filter((item) => item !== agentId);
      }
      return [...current, agentId];
    });
  }
'''

insert_block = '''
  function toggleDeploymentAgent(agentId: string) {
    setSelectedDeploymentAgents((current) => {
      if (current.includes(agentId)) {
        return current.filter((item) => item !== agentId);
      }
      return [...current, agentId];
    });
  }

  function selectAllDeploymentAgents() {
    setSelectedDeploymentAgents(ADMIN_AGENT_OPTIONS.map(([agentId]) => agentId));
  }

  function clearDeploymentAgents() {
    setSelectedDeploymentAgents([]);
  }

'''

if insert_block.strip() not in s:
    s = s.replace(insert_after, insert_after + insert_block)

selector_anchor = '''                  <input
                    value={deployEmail}
                    onChange={(event) => setDeployEmail(event.target.value)}
                    placeholder="Client email"
                    style={{
                      padding: 14,
                      borderRadius: 14,
                      background: "#020617",
                      color: "#fff",
                      border: "1px solid rgba(148,163,184,.22)",
                    }}
                  />
'''

selector_block = '''                  <input
                    value={deployEmail}
                    onChange={(event) => setDeployEmail(event.target.value)}
                    placeholder="Client email"
                    style={{
                      padding: 14,
                      borderRadius: 14,
                      background: "#020617",
                      color: "#fff",
                      border: "1px solid rgba(148,163,184,.22)",
                    }}
                  />

                  <div
                    style={{
                      border: "1px solid rgba(148,163,184,.22)",
                      borderRadius: 16,
                      padding: 14,
                      background: "#020617",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
                      <div>
                        <strong>Deploy client agents</strong>
                        <div style={{ color: "#94a3b8", fontSize: 12, marginTop: 4 }}>
                          Select exactly which agents this client can access. Manual Unlimited defaults to all agents.
                        </div>
                      </div>

                      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                        <button
                          type="button"
                          onClick={selectAllDeploymentAgents}
                          style={{
                            border: "1px solid rgba(34,197,94,.35)",
                            background: "rgba(34,197,94,.14)",
                            color: "#bbf7d0",
                            borderRadius: 10,
                            padding: "8px 10px",
                            fontWeight: 800,
                            cursor: "pointer",
                          }}
                        >
                          Select all
                        </button>

                        <button
                          type="button"
                          onClick={clearDeploymentAgents}
                          style={{
                            border: "1px solid rgba(248,113,113,.35)",
                            background: "rgba(248,113,113,.12)",
                            color: "#fecaca",
                            borderRadius: 10,
                            padding: "8px 10px",
                            fontWeight: 800,
                            cursor: "pointer",
                          }}
                        >
                          Clear
                        </button>
                      </div>
                    </div>

                    <div
                      style={{
                        display: "grid",
                        gridTemplateColumns: "repeat(auto-fit,minmax(210px,1fr))",
                        gap: 8,
                        maxHeight: 260,
                        overflow: "auto",
                        marginTop: 14,
                      }}
                    >
                      {ADMIN_AGENT_OPTIONS.map(([agentId, label]) => (
                        <label
                          key={`deploy-${agentId}`}
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: 10,
                            padding: 10,
                            borderRadius: 12,
                            background: selectedDeploymentAgents.includes(agentId)
                              ? "rgba(34,197,94,.18)"
                              : "rgba(15,23,42,.8)",
                            cursor: "pointer",
                          }}
                        >
                          <input
                            type="checkbox"
                            checked={selectedDeploymentAgents.includes(agentId)}
                            onChange={() => toggleDeploymentAgent(agentId)}
                          />
                          <span>{label}</span>
                        </label>
                      ))}
                    </div>

                    <div style={{ color: "#94a3b8", fontSize: 12, marginTop: 10 }}>
                      Deployment agents selected: {selectedDeploymentAgents.length}
                    </div>
                  </div>
'''

if selector_anchor not in s:
    raise SystemExit("DEPLOY_EMAIL_BLOCK_NOT_FOUND")

s = s.replace(selector_anchor, selector_block, 1)

s = s.replace(
    "active_agents: selectedAdminAgents,",
    "active_agents: selectedDeploymentAgents,"
)

FILE.write_text(s, encoding="utf-8")

print("ADMIN_DEPLOYMENT_AGENT_SELECTOR_FIXED")
print(f"Backup: {backup}")