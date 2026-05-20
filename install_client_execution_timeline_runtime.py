from pathlib import Path
from datetime import datetime

path = Path("frontend/src/app/client/page.tsx")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"client_page_before_execution_timeline_runtime_{timestamp}.tsx"
backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

text = path.read_text(encoding="utf-8")

# -------------------------------------------------------------------
# Insert execution event type.
# -------------------------------------------------------------------

type_block = '''
type ExecutionTimelineEvent = {
  event_id: string;
  created_at: string;
  agent_id: string;
  event_type: string;
  event_status: string;
  workflow_stage: string;
  action_type: string;
  execution_action?: string;
  approval_status?: string;
  execution_status?: string;
  quality_status?: string;
  title?: string;
  summary?: string;
};
'''

if "type ExecutionTimelineEvent =" not in text:
    insert_after = 'type LiveDeliverable = {'
    pos = text.find(insert_after)

    if pos != -1:
        next_type = text.find("};", pos)
        if next_type != -1:
            next_type += 2
            text = text[:next_type] + "\n\n" + type_block + text[next_type:]

# -------------------------------------------------------------------
# Insert state.
# -------------------------------------------------------------------

old_state = '  const [integrations, setIntegrations] = useState<ClientIntegration[]>([]);'
new_state = '''  const [integrations, setIntegrations] = useState<ClientIntegration[]>([]);
  const [executionTimeline, setExecutionTimeline] = useState<ExecutionTimelineEvent[]>([]);
  const [timelineLoading, setTimelineLoading] = useState(false);'''

text = text.replace(old_state, new_state)

# -------------------------------------------------------------------
# Insert timeline loader.
# -------------------------------------------------------------------

insert_after = '  async function loadIntegrations() {'

timeline_loader = '''

  async function loadExecutionTimeline() {
    try {
      setTimelineLoading(true);

      const response = await fetch(
        `${BACKEND_API_BASE}/client/execution-events?tenant_id=client_manual_admin&project_id=live_readiness_matrix&limit=20`,
        {
          cache: "no-store",
          headers: {
            "x-tenant-id": "client_manual_admin",
            "x-actor-role": "customer",
          },
        }
      );

      const data = await response.json();

      if (data?.success && Array.isArray(data.events)) {
        setExecutionTimeline(data.events);
      }
    } catch {
      setExecutionTimeline([]);
    } finally {
      setTimelineLoading(false);
    }
  }

'''

location = text.find(insert_after)

if location != -1 and "async function loadExecutionTimeline()" not in text:
    text = text[:location] + timeline_loader + text[location:]

# -------------------------------------------------------------------
# Auto-load timeline.
# -------------------------------------------------------------------

old_effect = '''  useEffect(() => {
    if (!toastMessage) return;'''

new_effect = '''  useEffect(() => {
    loadExecutionTimeline();
  }, []);

  useEffect(() => {
    if (!toastMessage) return;'''

text = text.replace(old_effect, new_effect)

# -------------------------------------------------------------------
# Replace fake timeline.
# -------------------------------------------------------------------

old_timeline = '''              {[
                [liveDeliverable?.created_at || "Live", liveDeliverable ? "Deliverable generated" : "Waiting for execution", selectedAgents.length ? getAgentDisplayName(selectedAgents[0]) : "Selected agent"],
                [reviewStatus === "approved" ? "Complete" : "Pending", reviewStatus === "approved" ? "Approved by client" : "Awaiting review", "Client workspace"],
              ].map(([time, event, actor]) => ('''

new_timeline = '''              {(executionTimeline.length
                ? executionTimeline.map((event) => [
                    event.created_at
                      ? new Date(event.created_at).toLocaleString()
                      : "Live",
                    event.title || event.event_type || "Execution event",
                    getAgentDisplayName(event.agent_id || "agent"),
                  ])
                : [
                    [
                      liveDeliverable?.created_at || "Live",
                      liveDeliverable
                        ? "Deliverable generated"
                        : timelineLoading
                          ? "Loading execution timeline"
                          : "Waiting for execution",
                      selectedAgents.length
                        ? getAgentDisplayName(selectedAgents[0])
                        : "Selected agent",
                    ],
                  ]).map(([time, event, actor]) => ('''

text = text.replace(old_timeline, new_timeline)

path.write_text(text, encoding="utf-8")

print("CLIENT_EXECUTION_TIMELINE_RUNTIME_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {path}")