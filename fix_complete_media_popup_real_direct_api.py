from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "frontend" / "src" / "components" / "UniversalCompleteMediaRunAgentPanel.tsx"
BACKUP_DIR = ROOT / "backups" / f"complete_media_popup_real_direct_api_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if not TARGET.exists():
    raise SystemExit(f"TARGET_NOT_FOUND: {TARGET}")

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP_DIR / TARGET.name)

text = TARGET.read_text(encoding="utf-8")

marker = 'data-complete-media-run-now="true"'
idx = text.find(marker)
if idx == -1:
    raise SystemExit("DIRECT_RUN_BUTTON_MARKER_NOT_FOUND")

button_start = text.rfind("<button", 0, idx)
if button_start == -1:
    raise SystemExit("DIRECT_RUN_BUTTON_START_NOT_FOUND")

button_text = text.find("Create complete media now", idx)
if button_text == -1:
    raise SystemExit("DIRECT_RUN_BUTTON_TEXT_NOT_FOUND")

button_end = text.find("</button>", button_text)
if button_end == -1:
    raise SystemExit("DIRECT_RUN_BUTTON_END_NOT_FOUND")

button_end += len("</button>")

new_button = r'''<button
                type="button"
                data-complete-media-run-now="true"
                data-complete-media-native-execution="true"
                onClick={async () => {
                  const button = document.querySelector('[data-complete-media-native-execution="true"]') as HTMLButtonElement | null;
                  const statusBox = document.querySelector('[data-complete-media-popup-status="true"]') as HTMLElement | null;

                  const setStatus = (message: string) => {
                    if (statusBox) statusBox.textContent = message;
                  };

                  try {
                    if (button) {
                      button.disabled = true;
                      button.textContent = "Creating complete media...";
                    }

                    setStatus("Creating complete media directly from this popup...");

                    const rawConfig = window.localStorage.getItem("universal_complete_media_config");
                    const savedConfig = rawConfig ? JSON.parse(rawConfig) : {};

                    const activeAgents = selectedAgents?.length
                      ? selectedAgents
                      : selectedAgent
                        ? [selectedAgent]
                        : [];

                    const selectedCreativeAgent =
                      savedConfig.agent_id ||
                      activeAgents.find((agent) =>
                        String(agent || "")
                          .toLowerCase()
                          .match(/creative|media|video|ugc|ad|campaign|social|image|content/)
                      ) ||
                      activeAgents[0] ||
                      "ugc_creative_agent";

                    const directConfig = {
                      ...savedConfig,
                      enabled: true,
                      run_direct_from_popup: true,
                      native_popup_execution: true,
                      creative_agent_direct_execution: true,
                      requested_from: "complete_media_popup",
                      requested_at: new Date().toISOString(),
                      agent_id: selectedCreativeAgent,
                      selected_agent: selectedCreativeAgent,
                      selected_agents: activeAgents,
                    };

                    window.localStorage.setItem("universal_complete_media_config", JSON.stringify(directConfig));
                    window.dispatchEvent(
                      new CustomEvent("universal-complete-media-config", {
                        detail: directConfig,
                      })
                    );

                    const endpoint =
                      mode === "admin"
                        ? "/api/admin-universal-complete-media"
                        : "/api/universal-complete-media";

                    const payload = {
                      source: "complete_media_popup",
                      requested_from: "complete_media_popup",
                      portal_mode: mode,
                      mode,
                      selected_agent: selectedCreativeAgent,
                      selected_agents: activeAgents,
                      agent_id: selectedCreativeAgent,
                      agent_ids: activeAgents,
                      business_profile: businessProfile || {},
                      complete_media_config: directConfig,
                      media_config: directConfig,
                      prompt: directConfig.prompt || "",
                      task: directConfig.prompt || "",
                      output_type: directConfig.output_type,
                      platform: directConfig.platform,
                      duration_seconds: directConfig.duration_seconds,
                      aspect_ratio: directConfig.aspect_ratio,
                      language: directConfig.language,
                      accent: directConfig.accent,
                      run_direct_from_popup: true,
                      native_popup_execution: true,
                      creative_agent_direct_execution: true,
                      customer_safe: mode !== "admin",
                      owner_admin_unrestricted: mode === "admin",
                    };

                    const response = await fetch(endpoint, {
                      method: "POST",
                      headers: {
                        "Content-Type": "application/json",
                        "X-Portal-Mode": mode,
                        "X-Requested-From": "complete_media_popup",
                      },
                      body: JSON.stringify(payload),
                    });

                    const result = await response.json().catch(() => ({
                      success: false,
                      error: "Invalid JSON response from complete media endpoint",
                    }));

                    if (!response.ok || result?.success === false) {
                      const message =
                        result?.error ||
                        result?.message ||
                        `Complete media request failed with HTTP ${response.status}`;
                      setStatus(message);
                      if (button) button.textContent = "Create complete media now";
                      return;
                    }

                    setStatus(
                      result?.media_job_id
                        ? `Complete media started from popup. Job ID: ${result.media_job_id}`
                        : "Complete media started directly from popup."
                    );

                    window.dispatchEvent(
                      new CustomEvent("universal-complete-media-run-now", {
                        detail: {
                          endpoint,
                          payload,
                          result,
                          native_popup_execution: true,
                        },
                      })
                    );

                    if (button) button.textContent = "Complete media started";
                  } catch (error) {
                    setStatus(
                      error instanceof Error
                        ? error.message
                        : "Complete media popup execution failed."
                    );
                    if (button) button.textContent = "Create complete media now";
                  } finally {
                    if (button) button.disabled = false;
                  }
                }}
                style={{
                  width: "fit-content",
                  border: "1px solid rgba(34,197,94,.36)",
                  borderRadius: 999,
                  padding: "10px 14px",
                  background:
                    mode === "admin"
                      ? "linear-gradient(135deg, rgba(34,197,94,.24), rgba(6,182,212,.16))"
                      : "linear-gradient(135deg, rgba(34,197,94,.12), rgba(79,70,229,.10))",
                  color: mode === "admin" ? "#bbf7d0" : "#166534",
                  fontWeight: 950,
                  cursor: "pointer",
                  boxShadow: "0 14px 34px rgba(15,23,42,.18)",
                }}
              >
                Create complete media now
              </button>'''

text = text[:button_start] + new_button + text[button_end:]

text = text.replace(
    "Saved. Click ",
    "Ready. Click "
)

text = text.replace(
    "Saved. Close this popup and click the main ",
    "Ready. Click "
)

text = text.replace(
    " to execute with these media settings, or close this popup without running.",
    " to create complete media directly from this popup."
)

text = text.replace(
    " button to execute with these media settings.",
    " to create complete media directly from this popup."
)

if 'data-complete-media-popup-status="true"' not in text:
    text = text.replace(
        'style={{ borderRadius: 16, padding: 12, background:',
        'data-complete-media-popup-status="true"\n                style={{ borderRadius: 16, padding: 12, background:',
        1,
    )

TARGET.write_text(text, encoding="utf-8")

verify = TARGET.read_text(encoding="utf-8")
required = [
    'data-complete-media-native-execution="true"',
    '"/api/admin-universal-complete-media"',
    '"/api/universal-complete-media"',
    "native_popup_execution",
    "creative_agent_direct_execution",
    "complete_media_popup",
]

missing = [item for item in required if item not in verify]
if missing:
    raise SystemExit(f"MISSING_REQUIRED_MARKERS: {missing}")

print("REAL_DIRECT_COMPLETE_MEDIA_POPUP_API_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {TARGET}")