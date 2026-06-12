from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "frontend" / "src" / "components" / "UniversalCompleteMediaRunAgentPanel.tsx"
BACKUP_DIR = ROOT / "backups" / f"popup_use_direct_media_provider_execute_multi_agent_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if not TARGET.exists():
    raise SystemExit(f"TARGET_NOT_FOUND: {TARGET}")

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP_DIR / TARGET.name)

text = TARGET.read_text(encoding="utf-8")

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

    const selectedCreativeAgents = resolvePopupSelectedAgents();
    const activeCreativeAgent = selectedCreativeAgents[0] || "ugc_creative_agent";
    const multiAgentMediaExecution = selectedCreativeAgents.length > 1;

    setStatusMessage(
      multiAgentMediaExecution
        ? `Creating complete media with ${selectedCreativeAgents.length} creative agents...`
        : `Creating complete media with ${activeCreativeAgent}...`
    );

    const directConfig = {
      ...mediaConfig,
      enabled: true,
      prompt: cleanPrompt,
      task: cleanPrompt,
      agent_id: activeCreativeAgent,
      selected_agent: activeCreativeAgent,
      selected_agents: selectedCreativeAgents,
      agent_ids: selectedCreativeAgents,
      requested_at: new Date().toISOString(),
      requested_from: "complete_media_popup",
      run_direct_from_popup: true,
      native_popup_execution: true,
      creative_agent_direct_execution: true,
      direct_media_provider_execute: true,
      multi_agent_media_execution: multiAgentMediaExecution,
      selected_agent_count: selectedCreativeAgents.length,
    };

    const provider =
      String(outputType || "").toLowerCase().includes("audio")
        ? "elevenlabs"
        : "runway";

    const mediaType =
      String(outputType || "").toLowerCase().includes("audio")
        ? "audio"
        : String(outputType || "").toLowerCase().includes("image")
          ? "image"
          : "video";

    const payload = {
      source: "complete_media_popup",
      requested_from: "complete_media_popup",
      portal_mode: portalMode,
      mode: portalMode,

      provider,
      provider_id: provider,
      media_type: mediaType,
      output_type: directConfig.output_type,
      platform: directConfig.platform,
      duration_seconds: directConfig.duration_seconds,
      aspect_ratio: directConfig.aspect_ratio,
      language: directConfig.language,
      accent: directConfig.accent,

      prompt: cleanPrompt,
      task: cleanPrompt,
      creative_brief: cleanPrompt,
      user_prompt: cleanPrompt,

      selected_agent: activeCreativeAgent,
      selected_agents: selectedCreativeAgents,
      agent_id: activeCreativeAgent,
      agent_ids: selectedCreativeAgents,
      lead_agent_id: activeCreativeAgent,

      business_profile: profile,
      complete_media_config: directConfig,
      media_config: directConfig,

      run_direct_from_popup: true,
      native_popup_execution: true,
      creative_agent_direct_execution: true,
      direct_media_provider_execute: true,
      multi_agent_media_execution: multiAgentMediaExecution,
      selected_agent_count: selectedCreativeAgents.length,

      customer_safe: portalMode !== "admin",
      owner_admin_unrestricted: portalMode === "admin",
    };

    try {
      window.localStorage.setItem(
        "universal_complete_media_config",
        JSON.stringify(directConfig)
      );
    } catch {}

    const endpoint =
      portalMode === "admin"
        ? "/api/admin-direct-media-provider-execute"
        : "/api/universal-complete-media";

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Portal-Mode": portalMode,
          "X-Requested-From": "complete_media_popup",
        },
        body: JSON.stringify(payload),
      });

      const result = await response.json().catch(() => ({
        success: false,
        error: "Invalid JSON response from direct media execution endpoint.",
      }));

      if (!response.ok || result?.success === false) {
        const errorText =
          result?.error ||
          result?.message ||
          result?.detail ||
          `Direct media request failed with HTTP ${response.status}.`;

        setStatusMessage(String(errorText));
        setRunning(false);
        return;
      }

      const jobId =
        result?.media_job_id ||
        result?.job_id ||
        result?.provider_job_id ||
        result?.execution_id ||
        result?.request_id ||
        result?.id ||
        "";

      setStatusMessage(
        jobId
          ? `Complete media started from popup. Lead agent: ${activeCreativeAgent}. Agents: ${selectedCreativeAgents.length}. Job ID: ${jobId}`
          : `Complete media started from popup. Lead agent: ${activeCreativeAgent}. Agents: ${selectedCreativeAgents.length}.`
      );

      onResult?.(result);

      window.dispatchEvent(
        new CustomEvent("universal-complete-media-run-now", {
          detail: {
            endpoint,
            payload,
            result,
            native_popup_execution: true,
            selected_agent: activeCreativeAgent,
            selected_agents: selectedCreativeAgents,
            multi_agent_media_execution: multiAgentMediaExecution,
          },
        })
      );
    } catch (error) {
      setStatusMessage(
        error instanceof Error
          ? error.message
          : "Complete media popup execution failed."
      );
    } finally {
      setRunning(false);
    }
  }
'''

text = text[:start] + new_function + text[end:]

TARGET.write_text(text, encoding="utf-8")

verify = TARGET.read_text(encoding="utf-8")
required = [
    "/api/admin-direct-media-provider-execute",
    "selectedCreativeAgents",
    "multi_agent_media_execution",
    "selected_agent_count",
    "lead_agent_id",
    "direct_media_provider_execute",
    "Create complete media now",
    "data-complete-media-agent-selector",
]

missing = [item for item in required if item not in verify]
if missing:
    raise SystemExit(f"MISSING_REQUIRED_MARKERS: {missing}")

print("POPUP_DIRECT_MEDIA_PROVIDER_EXECUTE_MULTI_AGENT_ROUTE_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {TARGET}")