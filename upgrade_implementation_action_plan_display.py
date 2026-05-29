from pathlib import Path
from datetime import datetime
import shutil

p = Path("frontend/src/app/admin/page.tsx")
backup = Path("backups") / f"implementation_action_plan_display_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(p, backup / "page.tsx")

s = p.read_text(encoding="utf-8")

s = s.replace(
'''                                  {(latestImplementationPlan.action_packets || []).slice(0, 6).map((packet: any) => (
                                    <div className="implementationPacket" key={packet.packet_id}>
                                      <b>{String(packet.recommended_agent || "agent").replaceAll("_", " ")}</b>
                                      <span>{packet.title}</span>
                                      <em>{packet.execution_status}</em>
                                    </div>
                                  ))}''',
'''                                  {(latestImplementationPlan.action_packets || []).slice(0, 10).map((packet: any) => (
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
)

s = s.replace(
'''        .implementationPacket {
          display: grid;
          grid-template-columns: 170px 1fr 170px;
          gap: 10px;
          align-items: start;
          padding: 10px;
          margin-top: 8px;
          border-radius: 14px;
          background: rgba(2, 6, 23, .56);
          border: 1px solid rgba(148, 163, 184, .18);
        }
        .implementationPacket b {
          color: #bfdbfe;
          font-size: 12px;
        }
        .implementationPacket span {
          color: #e5e7eb;
          font-size: 13px;
          line-height: 1.35;
        }
        .implementationPacket em {
          color: #facc15;
          font-style: normal;
          font-size: 12px;
          font-weight: 800;
        }''',
'''        .implementationPacket {
          display: grid;
          grid-template-columns: 190px minmax(260px, 1fr) 190px 190px;
          gap: 12px;
          align-items: start;
          padding: 14px;
          margin-top: 10px;
          border-radius: 16px;
          background: rgba(2, 6, 23, .66);
          border: 1px solid rgba(148, 163, 184, .18);
        }
        .implementationPacket small {
          display: block;
          color: #94a3b8;
          font-size: 10px;
          font-weight: 900;
          text-transform: uppercase;
          letter-spacing: .08em;
          margin-bottom: 5px;
        }
        .implementationPacket b {
          display: block;
          color: #bfdbfe;
          font-size: 13px;
          line-height: 1.3;
        }
        .implementationPacket span {
          display: block;
          color: #e5e7eb;
          font-size: 13px;
          line-height: 1.4;
        }
        .implementationPacket em {
          display: block;
          color: #facc15;
          font-style: normal;
          font-size: 12px;
          font-weight: 800;
          line-height: 1.35;
        }
        .packetActions {
          display: flex;
          flex-direction: column;
          gap: 7px;
        }
        .packetActions button {
          border: 1px solid rgba(20, 184, 166, .3);
          background: rgba(20, 184, 166, .1);
          color: #5eead4;
          border-radius: 999px;
          padding: 8px 10px;
          font-weight: 850;
          cursor: pointer;
          font-size: 12px;
        }'''
)

p.write_text(s, encoding="utf-8")

print("IMPLEMENTATION_ACTION_PLAN_DISPLAY_UPGRADED")
print(f"Backup: {backup}")
print(f"Updated: {p}")