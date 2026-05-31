from pathlib import Path
from datetime import datetime
import shutil

p = Path("frontend/src/app/admin/page.tsx")
backup = Path("backups") / f"packet_queue_visible_state_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(p, backup / "page.tsx")

s = p.read_text(encoding="utf-8")

s = s.replace(
    "const [latestImplementationPlan, setLatestImplementationPlan] = useState<any>(null);",
    """const [latestImplementationPlan, setLatestImplementationPlan] = useState<any>(null);
  const [queuedImplementationPackets, setQueuedImplementationPackets] = useState<any[]>([]);"""
)

anchor = '  const navItems = ["Overview", "Run Agent", "Deploy Clients", "Client Registry", "Runtime Health", "Provider Governance", "Orchestration", "Recovery", "Billing"];'

fn = r'''
  function queueImplementationPacket(packet: any) {
    const queuedPacket = {
      ...packet,
      queued_at: new Date().toLocaleString(),
      queue_status: "queued_for_governed_execution",
    };

    setQueuedImplementationPackets((prev) => [queuedPacket, ...prev].slice(0, 30));
    showToast("Packet queued for governed implementation execution.");
  }

'''

if fn.strip() not in s:
    s = s.replace(anchor, fn + "\n" + anchor)

s = s.replace(
    '<button onClick={() => showToast("Packet queued for governed execution review.")}>Queue</button>',
    '<button onClick={() => queueImplementationPacket(packet)}>Queue</button>'
)

s = s.replace(
'''["Implementation packets", latestImplementationPlan?.action_count || 0],
                ["Manual review items", latestImplementationPlan?.approval_summary?.approval_required_count || 0],''',
'''["Implementation packets", latestImplementationPlan?.action_count || 0],
                ["Queued packets", queuedImplementationPackets.length],
                ["Manual review items", latestImplementationPlan?.approval_summary?.approval_required_count || 0],'''
)

s = s.replace(
'''Review generated action packets and continue to implementation queue.''',
'''Review generated action packets and continue to implementation queue. Queued packets will appear below.'''
)

s = s.replace(
'''</Panel>

              <Panel title="Billing Intelligence" subtitle="Stripe package automation and credit lifecycle readiness.">''',
'''{queuedImplementationPackets.length ? (
                <div className="implementationPlanBox">
                  <strong>Queued Implementation Packets</strong>
                  <p>{queuedImplementationPackets.length} packet(s) queued for governed execution.</p>
                  {queuedImplementationPackets.slice(0, 8).map((packet: any) => (
                    <div className="implementationPacket" key={packet.packet_id + packet.queued_at}>
                      <div>
                        <small>Assigned agent</small>
                        <b>{String(packet.recommended_agent || "agent").replaceAll("_", " ")}</b>
                      </div>
                      <div>
                        <small>Queued implementation action</small>
                        <span>{packet.title}</span>
                      </div>
                      <div>
                        <small>Status</small>
                        <em>{packet.queue_status}</em>
                      </div>
                      <div className="packetActions">
                        <button onClick={() => showToast("Execution worker handoff is the next wiring step.")}>Run packet</button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : null}
            </Panel>

              <Panel title="Billing Intelligence" subtitle="Stripe package automation and credit lifecycle readiness.">'''
)

p.write_text(s, encoding="utf-8")

print("PACKET_QUEUE_VISIBLE_STATE_WIRED")
print(f"Backup: {backup}")
print(f"Updated: {p}")