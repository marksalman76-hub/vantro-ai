from pathlib import Path
from datetime import datetime
import shutil

p = Path("frontend/src/app/admin/page.tsx")
backup = Path("backups") / f"packet_run_live_execution_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(p, backup / "page.tsx")

s = p.read_text(encoding="utf-8")

s = s.replace(
    "const [queuedImplementationPackets, setQueuedImplementationPackets] = useState<any[]>([]);",
    """const [queuedImplementationPackets, setQueuedImplementationPackets] = useState<any[]>([]);
  const [completedImplementationRuns, setCompletedImplementationRuns] = useState<any[]>([]);"""
)

anchor = '  const navItems = ["Overview", "Run Agent", "Deploy Clients", "Client Registry", "Runtime Health", "Provider Governance", "Orchestration", "Recovery", "Billing"];'

fn = r'''
  async function runQueuedImplementationPacket(packet: any) {
    try {
      showToast("Running queued packet through governed live execution...");

      const response = await fetch("/api/admin-live-execution", {
        method: "POST",
        cache: "no-store",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          requested_agent: packet?.recommended_agent || "orchestration_agent",
          task: packet?.action || packet?.title || "Execute the approved implementation packet.",
        }),
      });

      const wrapper = await response.json();
      const data = wrapper?.data || wrapper;
      const execution = data?.execution || {};
      const adapter = execution?.adapter_result || {};
      const normalised = adapter?.normalised_response || {};
      const safeOutput = normalised?.safe_output || {};

      const completedRun = {
        packet_id: packet?.packet_id,
        agent_id: packet?.recommended_agent || "orchestration_agent",
        source_action: packet?.title,
        status: data?.success === true ? "completed" : "needs_review",
        provider: adapter?.provider_key || "openai",
        live_external_call_executed: adapter?.live_external_call_executed === true,
        latency_ms: adapter?.latency_ms || null,
        output:
          wrapper?.normalized_output ||
          safeOutput?.text ||
          data?.output?.generated_output ||
          data?.output?.output ||
          data?.output?.content ||
          data?.generated_output ||
          data?.result ||
          data?.message ||
          "No output returned.",
        completed_at: new Date().toLocaleString(),
      };

      setCompletedImplementationRuns((prev) => [completedRun, ...prev].slice(0, 30));
      showToast(data?.success === true ? "Implementation packet completed." : "Implementation packet needs review.");
    } catch {
      showToast("Queued packet execution failed before reaching live runtime.");
    }
  }

'''

if fn.strip() not in s:
    if anchor not in s:
        raise SystemExit("navItems anchor not found.")
    s = s.replace(anchor, fn + "\n" + anchor)

s = s.replace(
    '<button onClick={() => showToast("Execution worker handoff is the next wiring step.")}>Run packet</button>',
    '<button onClick={() => runQueuedImplementationPacket(packet)}>Run packet</button>'
)

s = s.replace(
'''["Queued packets", queuedImplementationPackets.length],
                ["Manual review items", latestImplementationPlan?.approval_summary?.approval_required_count || 0],''',
'''["Queued packets", queuedImplementationPackets.length],
                ["Completed packet runs", completedImplementationRuns.length],
                ["Manual review items", latestImplementationPlan?.approval_summary?.approval_required_count || 0],'''
)

s = s.replace(
'''{queuedImplementationPackets.length ? (
                <div className="implementationPlanBox">
                  <strong>Queued Implementation Packets</strong>''',
'''{completedImplementationRuns.length ? (
                <div className="implementationPlanBox">
                  <strong>Completed Implementation Runs</strong>
                  <p>{completedImplementationRuns.length} packet execution result(s) completed.</p>
                  {completedImplementationRuns.slice(0, 6).map((run: any) => (
                    <div className="implementationPacket" key={run.packet_id + run.completed_at}>
                      <div>
                        <small>Executed agent</small>
                        <b>{String(run.agent_id || "agent").replaceAll("_", " ")}</b>
                      </div>
                      <div>
                        <small>Execution result</small>
                        <span>{run.output}</span>
                      </div>
                      <div>
                        <small>Status</small>
                        <em>{run.status} · {run.provider} · {run.latency_ms ? `${run.latency_ms}ms` : "—"}</em>
                      </div>
                      <div className="packetActions">
                        <button onClick={() => navigator.clipboard.writeText(run.output || "")}>Copy result</button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : null}

              {queuedImplementationPackets.length ? (
                <div className="implementationPlanBox">
                  <strong>Queued Implementation Packets</strong>'''
)

p.write_text(s, encoding="utf-8")

print("PACKET_RUN_TO_LIVE_EXECUTION_WIRED")
print(f"Backup: {backup}")
print(f"Updated: {p}")