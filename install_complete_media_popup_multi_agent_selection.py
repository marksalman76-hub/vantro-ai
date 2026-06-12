from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "frontend" / "src" / "components" / "UniversalCompleteMediaRunAgentPanel.tsx"
BACKUP_DIR = ROOT / "backups" / f"complete_media_popup_multi_agent_selection_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if not TARGET.exists():
    raise SystemExit(f"TARGET_NOT_FOUND: {TARGET}")

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP_DIR / TARGET.name)

text = TARGET.read_text(encoding="utf-8")

# Add multi-agent state after selectedPopupAgent state.
state_marker = '  const [selectedPopupAgent, setSelectedPopupAgent] = useState("auto");\n'
if state_marker not in text:
    raise SystemExit("SELECTED_POPUP_AGENT_STATE_MARKER_NOT_FOUND")

if "selectedPopupAgents" not in text:
    text = text.replace(
        state_marker,
        state_marker
        + '  const [selectedPopupAgents, setSelectedPopupAgents] = useState<string[]>(["ugc_creative_agent"]);\n',
        1,
    )

# Add helper function before runCompleteMediaFromPopup.
run_marker = "  async function runCompleteMediaFromPopup() {"
if run_marker not in text:
    raise SystemExit("RUN_FUNCTION_MARKER_NOT_FOUND")

if "function resolvePopupSelectedAgents()" not in text:
    helper = r'''
  function resolvePopupSelectedAgents() {
    const availableCreativeAgents =
      agents.length > 0 ? agents : DEFAULT_CREATIVE_AGENTS;

    if (selectedPopupAgent === "auto") {
      const bestAgent =
        availableCreativeAgents.find(isCreativeAgent) ||
        availableCreativeAgents[0] ||
        "ugc_creative_agent";

      return [bestAgent];
    }

    if (selectedPopupAgent === "all") {
      const allCreativeAgents =
        availableCreativeAgents.filter(isCreativeAgent).length > 0
          ? availableCreativeAgents.filter(isCreativeAgent)
          : DEFAULT_CREATIVE_AGENTS;

      return Array.from(new Set(allCreativeAgents));
    }

    if (selectedPopupAgent === "custom") {
      const customAgents =
        selectedPopupAgents.length > 0
          ? selectedPopupAgents
          : ["ugc_creative_agent"];

      return Array.from(new Set(customAgents));
    }

    return [selectedPopupAgent || "ugc_creative_agent"];
  }

  function togglePopupAgent(agentId: string) {
    setSelectedPopupAgents((current) => {
      if (current.includes(agentId)) {
        const next = current.filter((agent) => agent !== agentId);
        return next.length > 0 ? next : ["ugc_creative_agent"];
      }

      return Array.from(new Set([...current, agentId]));
    });
  }

'''
    text = text.replace(run_marker, helper + run_marker, 1)

# Replace single activeCreativeAgent blocks inside run function.
old_active_block = r'''    const activeCreativeAgent =
      selectedPopupAgent && selectedPopupAgent !== "auto"
        ? selectedPopupAgent
        : primaryAgent || "ugc_creative_agent";'''

new_active_block = r'''    const selectedCreativeAgents = resolvePopupSelectedAgents();
    const activeCreativeAgent = selectedCreativeAgents[0] || "ugc_creative_agent";
    const multiAgentMediaExecution = selectedCreativeAgents.length > 1;'''

if old_active_block in text:
    text = text.replace(old_active_block, new_active_block)
else:
    print("WARNING_ACTIVE_AGENT_BLOCK_NOT_FOUND_OR_ALREADY_CHANGED")

# Replace single selected agent arrays with selectedCreativeAgents in run function.
text = text.replace("selected_agents: [activeCreativeAgent]", "selected_agents: selectedCreativeAgents")
text = text.replace("agent_ids: [activeCreativeAgent]", "agent_ids: selectedCreativeAgents")

# Add multi-agent flags after creative direct execution markers.
text = text.replace(
    "creative_agent_direct_execution: true,",
    "creative_agent_direct_execution: true,\n      multi_agent_media_execution: multiAgentMediaExecution,\n      selected_agent_count: selectedCreativeAgents.length,",
)

# The global replacement above may affect mediaConfig useMemo before these names exist.
# Repair any accidental insertions outside run function by replacing invalid references in the mediaConfig useMemo.
text = text.replace(
    "creative_agent_direct_execution: true,\n      multi_agent_media_execution: multiAgentMediaExecution,\n      selected_agent_count: selectedCreativeAgents.length,\n      requested_from: \"complete_media_popup\",",
    "creative_agent_direct_execution: true,\n      requested_from: \"complete_media_popup\",",
    1,
)

# Replace selector UI with mode selector + custom multi-agent checkboxes.
selector_start = text.find('              <label\n                data-complete-media-agent-selector="true"')
if selector_start == -1:
    raise SystemExit("AGENT_SELECTOR_START_NOT_FOUND")

selector_end_marker = "              </label>\n\n              <label"
selector_end = text.find(selector_end_marker, selector_start)
if selector_end == -1:
    raise SystemExit("AGENT_SELECTOR_END_NOT_FOUND")

selector_end += len("              </label>\n\n")

new_selector = r'''              <div
                data-complete-media-agent-selector="true"
                style={{
                  display: "grid",
                  gap: 10,
                  borderRadius: 16,
                  padding: 12,
                  border: "1px solid rgba(129,140,248,.22)",
                  background:
                    portalMode === "admin"
                      ? "rgba(15,23,42,.42)"
                      : "rgba(248,250,252,.9)",
                }}
              >
                <label
                  style={{
                    display: "grid",
                    gap: 6,
                    fontSize: 12.5,
                    fontWeight: 850,
                    color: portalMode === "admin" ? "#cbd5e1" : "#0f172a",
                  }}
                >
                  Agent selection mode
                  <select
                    value={selectedPopupAgent}
                    onChange={(event) => setSelectedPopupAgent(event.target.value)}
                    style={fieldStyle(portalMode)}
                  >
                    <option value="auto">Auto-select best creative agent</option>
                    <option value="all">Use all creative agents</option>
                    <option value="custom">Select multiple creative agents</option>
                    {POPUP_CREATIVE_AGENT_OPTIONS.filter((agent) => agent.value !== "auto").map((agent) => (
                      <option key={agent.value} value={agent.value}>
                        Single: {agent.label}
                      </option>
                    ))}
                  </select>
                </label>

                {selectedPopupAgent === "custom" ? (
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))",
                      gap: 8,
                    }}
                  >
                    {POPUP_CREATIVE_AGENT_OPTIONS.filter((agent) => agent.value !== "auto").map((agent) => (
                      <label
                        key={agent.value}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 8,
                          borderRadius: 12,
                          padding: "8px 10px",
                          border: "1px solid rgba(148,163,184,.24)",
                          color: portalMode === "admin" ? "#e5e7eb" : "#0f172a",
                          fontSize: 12.5,
                          fontWeight: 800,
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={selectedPopupAgents.includes(agent.value)}
                          onChange={() => togglePopupAgent(agent.value)}
                        />
                        {agent.label}
                      </label>
                    ))}
                  </div>
                ) : null}

                <div
                  style={{
                    color: portalMode === "admin" ? "#94a3b8" : "#64748b",
                    fontSize: 12,
                    lineHeight: 1.5,
                  }}
                >
                  Selected for this media run: {resolvePopupSelectedAgents().join(", ")}
                </div>
              </div>

'''

text = text[:selector_start] + new_selector + text[selector_end:]

# Improve status message to include multi-agent possibility.
text = text.replace(
    "Choose the creative agent inside this popup, enter the media prompt, then click Create complete media now. You do not need to use the main Run Agent section.",
    "Choose one or more creative agents inside this popup, enter the media prompt, then click Create complete media now. You do not need to use the main Run Agent section."
)

TARGET.write_text(text, encoding="utf-8")

verify = TARGET.read_text(encoding="utf-8")
required = [
    "selectedPopupAgents",
    "resolvePopupSelectedAgents",
    "togglePopupAgent",
    "multi_agent_media_execution",
    "selected_agent_count",
    "Use all creative agents",
    "Select multiple creative agents",
    "Selected for this media run",
]

missing = [item for item in required if item not in verify]
if missing:
    raise SystemExit(f"MISSING_REQUIRED_MARKERS: {missing}")

print("COMPLETE_MEDIA_POPUP_MULTI_AGENT_SELECTION_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {TARGET}")