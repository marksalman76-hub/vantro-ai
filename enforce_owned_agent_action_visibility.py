from pathlib import Path
from datetime import datetime
import shutil

p = Path("frontend/src/app/admin/page.tsx")
backup = Path("backups") / f"owned_agent_action_visibility_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(p, backup / "page.tsx")

s = p.read_text(encoding="utf-8")

old = '''                                  {(latestImplementationPlan.action_packets || []).slice(0, 10).map((packet: any) => (
                                    <div className="implementationPacket" key={packet.packet_id}>
                                      <div>
                                        <small>Assigned agent</small>
                                        <b>{String(packet.recommended_agent || "agent").replaceAll("_", " ")}</b>
                                      </div>
                                      <div>
                                        <small>Implementation action</small>
                                        <span>{packet.title}</span>
                                      </div>
                                      <div>
                                        <small>Risk / status</small>
                                        <em>{packet.risk_level || "medium"} · {packet.execution_status}</em>
                                      </div>
                                      <div className="packetActions">
                                        <button onClick={() => showToast("Packet queued for governed execution review.")}>Queue</button>
                                        <button onClick={() => showToast("Packet sent to client visibility queue.")}>Send to client</button>
                                      </div>
                                    </div>
                                  ))}'''

new = '''                                  {(latestImplementationPlan.action_packets || []).slice(0, 10).map((packet: any) => {
                                    const recommendedAgent = String(packet.recommended_agent || "agent");
                                    const isAdminOrEnterprise = true;
                                    const ownedAgents = selectedDeploy.length ? selectedDeploy : selectedRun;
                                    const agentOwned = isAdminOrEnterprise || ownedAgents.includes(recommendedAgent);

                                    return (
                                      <div className={agentOwned ? "implementationPacket" : "implementationPacket locked"} key={packet.packet_id}>
                                        <div>
                                          <small>{agentOwned ? "Assigned agent" : "Recommended specialist agent"}</small>
                                          <b>{recommendedAgent.replaceAll("_", " ")}</b>
                                        </div>

                                        <div>
                                          <small>{agentOwned ? "Implementation action" : "Why recommended"}</small>
                                          <span>
                                            {agentOwned
                                              ? packet.title
                                              : "This specialist agent could unlock additional implementation capacity for this outcome."}
                                          </span>
                                        </div>

                                        <div>
                                          <small>{agentOwned ? "Risk / status" : "Package status"}</small>
                                          <em>
                                            {agentOwned
                                              ? `${packet.risk_level || "medium"} · ${packet.execution_status}`
                                              : "Upgrade required · task hidden"}
                                          </em>
                                        </div>

                                        <div className="packetActions">
                                          {agentOwned ? (
                                            <>
                                              <button onClick={() => showToast("Packet queued for governed execution review.")}>Queue</button>
                                              <button onClick={() => showToast("Packet sent to client visibility queue.")}>Send to client</button>
                                            </>
                                          ) : (
                                            <>
                                              <button onClick={() => showToast("Upgrade recommendation saved.")}>Recommend upgrade</button>
                                              <button onClick={() => showToast("Implementation task is hidden until this agent is purchased.")}>Preview value</button>
                                            </>
                                          )}
                                        </div>
                                      </div>
                                    );
                                  })}'''

if old not in s:
    raise SystemExit("Implementation packet render block not found. No changes made.")

s = s.replace(old, new)

s = s.replace(
'''        .implementationPacket {
          display: grid;''',
'''        .implementationPacket.locked {
          border-color: rgba(250, 204, 21, .35);
          background: rgba(113, 63, 18, .16);
        }
        .implementationPacket {
          display: grid;'''
)

p.write_text(s, encoding="utf-8")

print("OWNED_AGENT_ACTION_VISIBILITY_ENFORCED")
print(f"Backup: {backup}")
print(f"Updated: {p}")