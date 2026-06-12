from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "frontend" / "src" / "components" / "UniversalCompleteMediaRunAgentPanel.tsx"
BACKUP_DIR = ROOT / "backups" / f"self_contained_complete_media_popup_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if not TARGET.exists():
    raise SystemExit(f"TARGET_NOT_FOUND: {TARGET}")

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP_DIR / TARGET.name)

text = TARGET.read_text(encoding="utf-8")

# Keep current component, but make the UX self-contained and make execution more reliable.

# 1. Remove any old checkbox label if it survived.
text = text.replace(
    "Create complete media when Run Agent is clicked",
    "Create complete media now"
)

# 2. Replace misleading wording.
text = text.replace(
    "Run Agent media options",
    "Create Media"
)

text = text.replace(
    "Complete media output",
    "Create complete media"
)

text = text.replace(
    "Configure the media output here, then click Create complete media now. This runs directly from the popup without using the main Run Agent section.",
    "Choose the creative agent inside this popup, enter the media prompt, then click Create complete media now. You do not need to use the main Run Agent section."
)

text = text.replace(
    "Configure optional media output here, then click Create complete media now to run directly from this popup.",
    "Choose the creative agent inside this popup, enter the media prompt, then click Create complete media now."
)

# 3. Ensure agent options exist.
if "const POPUP_CREATIVE_AGENT_OPTIONS" not in text:
    insert_after = "const DEFAULT_CREATIVE_AGENTS = ["
    idx = text.find(insert_after)
    if idx == -1:
        raise SystemExit("DEFAULT_CREATIVE_AGENTS_MARKER_NOT_FOUND")

    end_idx = text.find("];", idx)
    if end_idx == -1:
        raise SystemExit("DEFAULT_CREATIVE_AGENTS_END_NOT_FOUND")

    end_idx += 2

    agent_options = '''

const POPUP_CREATIVE_AGENT_OPTIONS = [
  { value: "auto", label: "Auto-select best creative agent" },
  { value: "ugc_creative_agent", label: "UGC Creative Agent" },
  { value: "social_media_manager_content_creator_agent", label: "Social Media / Content Creator Agent" },
  { value: "ad_creative_agent", label: "Ad Creative Agent" },
  { value: "campaign_launch_agent", label: "Campaign Launch Agent" },
  { value: "creative_rotation_agent", label: "Creative Rotation Agent" },
  { value: "product_image_direction_agent", label: "Product Image Direction Agent" },
  { value: "product_copywriting_agent", label: "Product Copywriting Agent" },
  { value: "marketing_specialist_agent", label: "Marketing Specialist Agent" },
];
'''
    text = text[:end_idx] + agent_options + text[end_idx:]

# 4. Add selectedPopupAgent state if missing.
if "const [selectedPopupAgent, setSelectedPopupAgent]" not in text:
    marker = 'const [statusMessage, setStatusMessage] = useState('
    idx = text.find(marker)
    if idx == -1:
        raise SystemExit("STATUS_STATE_MARKER_NOT_FOUND")

    line_end = text.find(");", idx)
    if line_end == -1:
        raise SystemExit("STATUS_STATE_END_NOT_FOUND")

    line_end += 2

    text = (
        text[:line_end]
        + '\n  const [selectedPopupAgent, setSelectedPopupAgent] = useState("auto");\n'
        + text[line_end:]
    )

# 5. Make primaryAgent use popup selection.
old_primary = '''  const primaryAgent =
    agents.find(isCreativeAgent) || agents[0] || "ugc_creative_agent";'''

new_primary = '''  const autoSelectedCreativeAgent =
    agents.find(isCreativeAgent) || agents[0] || "ugc_creative_agent";

  const primaryAgent =
    selectedPopupAgent && selectedPopupAgent !== "auto"
      ? selectedPopupAgent
      : autoSelectedCreativeAgent;'''

if old_primary in text:
    text = text.replace(old_primary, new_primary)

# 6. Add selectedPopupAgent to useMemo dependencies if needed.
text = text.replace(
    "primaryAgent,\n      agents,",
    "primaryAgent,\n      selectedPopupAgent,\n      agents,"
)

# 7. Insert agent selector before media prompt if missing.
if "data-complete-media-agent-selector" not in text:
    media_prompt_label = '''              <label
                style={{
                  display: "grid",
                  gap: 6,
                  fontSize: 12.5,
                  fontWeight: 850,
                  color: portalMode === "admin" ? "#cbd5e1" : "#0f172a",
                }}
              >
                Media prompt'''

    if media_prompt_label not in text:
        raise SystemExit("MEDIA_PROMPT_LABEL_MARKER_NOT_FOUND")

    selector = '''              <label
                data-complete-media-agent-selector="true"
                style={{
                  display: "grid",
                  gap: 6,
                  fontSize: 12.5,
                  fontWeight: 850,
                  color: portalMode === "admin" ? "#cbd5e1" : "#0f172a",
                }}
              >
                Creative agent
                <select
                  value={selectedPopupAgent}
                  onChange={(event) => setSelectedPopupAgent(event.target.value)}
                  style={fieldStyle(portalMode)}
                >
                  {POPUP_CREATIVE_AGENT_OPTIONS.map((agent) => (
                    <option key={agent.value} value={agent.value}>
                      {agent.label}
                    </option>
                  ))}
                </select>
              </label>

'''
    text = text.replace(media_prompt_label, selector + media_prompt_label)

# 8. Replace execution function body with fallback route execution.
start_marker = "  async function runCompleteMediaFromPopup() {"
start = text.find(start_marker)
if start == -1:
    raise SystemExit("RUN_FUNCTION_START_NOT_FOUND")

end_marker = "\n  if (!shouldShow) return null;"
end = text.find(end_marker, start)
if end == -1:
    raise SystemExit("RUN_FUNCTION_END_NOT_FOUND")

new_function = r'''  async function runCompleteMediaFromPopup() {
    const cleanPrompt = String(prompt || "").trim();

    if (!cleanPrompt) {
      setStatusMessage("Add a media prompt first, then click Create complete media now.");
      return;
    }

    setRunning(true);
    setStatusMessage("Creating complete media directly from this popup...");

    const activeCreativeAgent =
      selectedPopupAgent && selectedPopupAgent !== "auto"
        ? selectedPopupAgent
        : primaryAgent || "ugc_creative_agent";

    const directConfig = {
      ...mediaConfig,
      enabled: true,
      prompt: cleanPrompt,
      task: cleanPrompt,
      agent_id: activeCreativeAgent,
      selected_agent: activeCreativeAgent,
      selected_agents: [activeCreativeAgent],
      requested_at: new Date().toISOString(),
      requested_from: "complete_media_popup",
      run_direct_from_popup: true,
      native_popup_execution: true,
      creative_agent_direct_execution: true,
    };

    const mediaPayload = {
      source: "complete_media_popup",
      requested_from: "complete_media_popup",
      portal_mode: portalMode,
      mode: portalMode,
      selected_agent: activeCreativeAgent,
      selected_agents: [activeCreativeAgent],
      agent_id: activeCreativeAgent,
      agent_ids: [activeCreativeAgent],
      business_profile: profile,
      complete_media_config: directConfig,
      media_config: directConfig,
      prompt: cleanPrompt,
      task: cleanPrompt,
      output_type: directConfig.output_type,
      platform: directConfig.platform,
      duration_seconds: directConfig.duration_seconds,
      aspect_ratio: directConfig.aspect_ratio,
      language: directConfig.language,
      accent: directConfig.accent,
      run_direct_from_popup: true,
      native_popup_execution: true,
      creative_agent_direct_execution: true,
      customer_safe: portalMode !== "admin",
      owner_admin_unrestricted: portalMode === "admin",
    };

    const governedRunAgentPayload = {
      source: "complete_media_popup",
      requested_from: "complete_media_popup",
      action: "run_agent",
      execution_action: "governed_live_provider_generation",
      action_type: "governed_live_provider_generation",
      agent_id: activeCreativeAgent,
      selected_agent: activeCreativeAgent,
      selected_agents: [activeCreativeAgent],
      agent_ids: [activeCreativeAgent],
      task: cleanPrompt,
      prompt: cleanPrompt,
      business_profile: profile,
      complete_media_config: directConfig,
      media_config: directConfig,
      run_direct_from_popup: true,
      native_popup_execution: true,
      creative_agent_direct_execution: true,
      owner_admin_unrestricted: portalMode === "admin",
      customer_safe: portalMode !== "admin",
    };

    const endpointAttempts =
      portalMode === "admin"
        ? [
            {
              endpoint: "/api/admin-universal-complete-media",
              payload: mediaPayload,
            },
            {
              endpoint: "/api/admin-deployment-control",
              payload: governedRunAgentPayload,
            },
            {
              endpoint: "/api/run-agent",
              payload: governedRunAgentPayload,
            },
          ]
        : [
            {
              endpoint: "/api/universal-complete-media",
              payload: mediaPayload,
            },
            {
              endpoint: "/api/run-agent",
              payload: governedRunAgentPayload,
            },
          ];

    try {
      window.localStorage.setItem(
        "universal_complete_media_config",
        JSON.stringify(directConfig)
      );
    } catch {}

    const failedAttempts: string[] = [];

    for (const attempt of endpointAttempts) {
      try {
        setStatusMessage(`Creating complete media through ${attempt.endpoint}...`);

        const response = await fetch(attempt.endpoint, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Portal-Mode": portalMode,
            "X-Requested-From": "complete_media_popup",
          },
          body: JSON.stringify(attempt.payload),
        });

        const result = await response.json().catch(() => ({
          success: false,
          error: "Invalid JSON response from execution endpoint.",
        }));

        const errorText = String(
          result?.error ||
            result?.message ||
            result?.detail ||
            result?.status ||
            ""
        );

        const bridgeFailed =
          errorText.includes("direct_media_provider_bridge_failed") ||
          errorText.includes("bridge_failed");

        if (!response.ok || result?.success === false || bridgeFailed) {
          failedAttempts.push(`${attempt.endpoint}: ${errorText || response.status}`);
          continue;
        }

        const jobId =
          result?.media_job_id ||
          result?.job_id ||
          result?.execution_id ||
          result?.request_id ||
          result?.id ||
          "";

        setStatusMessage(
          jobId
            ? `Complete media started from popup with ${activeCreativeAgent}. Job ID: ${jobId}`
            : `Complete media started from popup with ${activeCreativeAgent}.`
        );

        onResult?.(result);

        window.dispatchEvent(
          new CustomEvent("universal-complete-media-run-now", {
            detail: {
              endpoint: attempt.endpoint,
              payload: attempt.payload,
              result,
              native_popup_execution: true,
              selected_agent: activeCreativeAgent,
            },
          })
        );

        setRunning(false);
        return;
      } catch (error) {
        failedAttempts.push(
          `${attempt.endpoint}: ${
            error instanceof Error ? error.message : "request failed"
          }`
        );
      }
    }

    setStatusMessage(
      `Complete media could not start. Tried: ${failedAttempts.join(" | ")}`
    );
    setRunning(false);
  }
'''

text = text[:start] + new_function + text[end:]

TARGET.write_text(text, encoding="utf-8")

verify = TARGET.read_text(encoding="utf-8")
required = [
    "data-complete-media-agent-selector",
    "POPUP_CREATIVE_AGENT_OPTIONS",
    "selectedPopupAgent",
    "/api/admin-deployment-control",
    "/api/run-agent",
    "Complete media could not start. Tried:",
    "Auto-select best creative agent",
]

missing = [item for item in required if item not in verify]
if missing:
    raise SystemExit(f"MISSING_REQUIRED_MARKERS: {missing}")

print("SELF_CONTAINED_COMPLETE_MEDIA_POPUP_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {TARGET}")