from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "frontend" / "src" / "components" / "UniversalCompleteMediaRunAgentPanel.tsx"
BACKUP_DIR = ROOT / "backups" / f"popup_to_universal_complete_media_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

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

    const lowerPrompt = cleanPrompt.toLowerCase();
    const productRelevant =
      lowerPrompt.includes("product") ||
      lowerPrompt.includes("skincare") ||
      lowerPrompt.includes("cream") ||
      lowerPrompt.includes("serum") ||
      lowerPrompt.includes("bottle") ||
      lowerPrompt.includes("package") ||
      lowerPrompt.includes("packaging") ||
      lowerPrompt.includes("item") ||
      lowerPrompt.includes("using a") ||
      lowerPrompt.includes("holding a");

    const continuityGuardrails = [
      "Maintain consistent subjects, hands, faces, clothing, props, backgrounds, reflections, object positions, camera movement, and scene physics across the full clip.",
      "Avoid disappearing objects, morphing props, warped fingers, impossible reflections, mismatched hand movement, sudden object teleporting, or visual continuity breaks.",
      "Keep physical interactions realistic and temporally consistent.",
      "When voiceover or narration is requested, pace the visual action so it can align naturally with the spoken script.",
      productRelevant
        ? "Because this prompt involves a product or handled object, keep the product visible and visually consistent, maintain accurate hand-product contact, and keep mirror/reflection placement consistent when reflections appear."
        : "",
    ]
      .filter(Boolean)
      .join(" ");

    const directConfig = {
      ...mediaConfig,
      enabled: true,
      prompt: cleanPrompt,
      task: cleanPrompt,
      visual_quality_guardrails: continuityGuardrails,
      agent_id: activeCreativeAgent,
      selected_agent: activeCreativeAgent,
      selected_agents: selectedCreativeAgents,
      agent_ids: selectedCreativeAgents,
      video_provider: "runway",
      audio_provider: "elevenlabs",
      requested_at: new Date().toISOString(),
      requested_from: "complete_media_popup",
      run_direct_from_popup: true,
      native_popup_execution: true,
      creative_agent_direct_execution: true,
      universal_complete_media_workflow: true,
      one_prompt_complete_media: true,
      multi_agent_media_execution: multiAgentMediaExecution,
      selected_agent_count: selectedCreativeAgents.length,
    };

    const payload = {
      source: "complete_media_popup",
      requested_from: "complete_media_popup",
      portal_mode: portalMode,
      mode: portalMode,

      prompt: cleanPrompt,
      task: cleanPrompt,
      creative_brief: cleanPrompt,
      user_prompt: cleanPrompt,
      visual_quality_guardrails: continuityGuardrails,

      selected_agent: activeCreativeAgent,
      selected_agents: selectedCreativeAgents,
      agent_id: activeCreativeAgent,
      agent_ids: selectedCreativeAgents,
      lead_agent_id: activeCreativeAgent,

      business_profile: profile,
      complete_media_config: directConfig,
      media_config: directConfig,

      output_type: directConfig.output_type || outputType,
      platform: directConfig.platform || platform,
      duration_seconds: directConfig.duration_seconds || durationSeconds,
      aspect_ratio: directConfig.aspect_ratio || aspectRatio,
      language: directConfig.language || language,
      accent: directConfig.accent || accent,
      tone: directConfig.tone,
      voice_style: directConfig.voice_style,
      call_to_action: directConfig.call_to_action,

      video_provider: "runway",
      audio_provider: "elevenlabs",
      provider: "universal_complete_media_workflow",
      media_type: "complete_video",
      asset_type: "video",

      run_direct_from_popup: true,
      native_popup_execution: true,
      creative_agent_direct_execution: true,
      universal_complete_media_workflow: true,
      one_prompt_complete_media: true,
      multi_agent_media_execution: multiAgentMediaExecution,
      selected_agent_count: selectedCreativeAgents.length,

      owner_approved: portalMode === "admin",
      owner_approval_granted: portalMode === "admin",
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
        ? "/api/admin-universal-complete-media"
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
        error: "Invalid JSON response from universal complete media endpoint.",
      }));

      if (!response.ok || result?.success === false) {
        const errorText =
          result?.error ||
          result?.message ||
          result?.detail ||
          `Universal complete media request failed with HTTP ${response.status}.`;

        setStatusMessage(String(errorText));
        setRunning(false);
        return;
      }

      const extractedPopupResult = applyPopupMediaJobResult(result);

      const jobId =
        extractedPopupResult.jobId ||
        result?.media_job_id ||
        result?.job_id ||
        result?.provider_job_id ||
        result?.execution_id ||
        result?.request_id ||
        result?.id ||
        "";

      setStatusMessage(
        jobId
          ? `Complete media workflow started. Lead agent: ${activeCreativeAgent}. Agents: ${selectedCreativeAgents.length}. Job ID: ${jobId}`
          : `Complete media workflow started. Lead agent: ${activeCreativeAgent}. Agents: ${selectedCreativeAgents.length}.`
      );

      if (jobId) {
        setTimeout(() => {
          void checkPopupMediaJobStatus(jobId);
        }, 1500);
      }

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
            universal_complete_media_workflow: true,
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
    "/api/admin-universal-complete-media",
    "/api/universal-complete-media",
    "universal_complete_media_workflow",
    "one_prompt_complete_media",
    "video_provider: \"runway\"",
    "audio_provider: \"elevenlabs\"",
    "visual_quality_guardrails",
    "multi_agent_media_execution",
    "selected_agent_count",
]

missing = [item for item in required if item not in verify]
if missing:
    raise SystemExit(f"MISSING_REQUIRED_MARKERS: {missing}")

print("POPUP_ROUTED_TO_UNIVERSAL_COMPLETE_MEDIA_WORKFLOW")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {TARGET}")