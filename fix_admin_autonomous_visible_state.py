from pathlib import Path

p = Path("frontend/src/app/admin/live-execution/page.tsx")
s = p.read_text(encoding="utf-8")

s = s.replace(
'''  const outputText =
    safeOutput?.text ||
    result?.output?.generated_output ||
    result?.output?.output ||
    result?.output?.content ||
    "";''',
'''  const outputText = result ? extractAutonomousDeliverable(result) : "";'''
)

s = s.replace(
'''  const liveCall = adapter?.live_external_call_executed === true;''',
'''  const firstAutonomousResult = getAutonomousFirstResult(result);
  const liveCall = Boolean(result?.completed_results?.length || firstAutonomousResult?.performed_actual_action || firstAutonomousResult?.delegate_execution === "executed");'''
)

s = s.replace(
'''{["Live output", agentName(agent), liveCall ? "OpenAI verified" : "Provider pending", "Admin-ready"].map((tag) => (''',
'''{["Autonomous output", agentName(agent), liveCall ? "Autonomous route verified" : "Route pending", "Admin-ready"].map((tag) => ('''
)

s = s.replace(
'''                  ["Provider", adapter?.provider_key || (running ? "Running" : "—")],
                  ["Latency", adapter?.latency_ms ? `${adapter.latency_ms}ms` : running ? "Measuring" : "—"],
                  ["Memory", result?.memory?.memory_saved ? "Saved" : running ? "Pending" : "—"],
                  ["Safe", adapter?.customer_safe ? "True" : running ? "Pending" : "—"],''',
'''                  ["Provider", result ? autonomousProviderLabel(result) : running ? "Running" : "—"],
                  ["Latency", result ? autonomousLatencyLabel(result) : running ? "Measuring" : "—"],
                  ["Memory", result?.completed_results?.length || result?.queued_results?.length || result?.blocked_results?.length ? "Saved" : running ? "Pending" : "—"],
                  ["Safe", result ? autonomousSafeLabel(result) : running ? "Pending" : "—"],'''
)

p.write_text(s, encoding="utf-8")
print("ADMIN_AUTONOMOUS_VISIBLE_STATE_FIXED")