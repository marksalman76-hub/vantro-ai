from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path.cwd()
TARGET = ROOT / "frontend" / "src" / "components" / "UniversalCompleteMediaRunAgentPanel.tsx"
BACKUP_DIR = ROOT / "backups" / f"popup_universal_media_status_polling_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if not TARGET.exists():
    raise SystemExit(f"TARGET_NOT_FOUND: {TARGET}")

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP_DIR / TARGET.name)

text = TARGET.read_text(encoding="utf-8")

start_marker = "  async function checkPopupMediaJobStatus(jobIdOverride?: string) {"
start = text.find(start_marker)
if start == -1:
    raise SystemExit("CHECK_POPUP_MEDIA_JOB_STATUS_START_NOT_FOUND")

next_function = re.search(r"\n  async function\s+[A-Za-z0-9_]+\s*\(", text[start + len(start_marker):])
if not next_function:
    raise SystemExit("NEXT_ASYNC_FUNCTION_AFTER_STATUS_CHECK_NOT_FOUND")

end = start + len(start_marker) + next_function.start()

new_function = r'''  async function checkPopupMediaJobStatus(jobIdOverride?: string) {
    const jobId = jobIdOverride || popupMediaJobId;

    if (!jobId) {
      setStatusMessage("No media job ID is available yet.");
      return;
    }

    const isUniversalCompleteMediaJob = String(jobId).startsWith("universal_complete_media_job_");

    const statusEndpoints =
      portalMode === "admin"
        ? [
            `/api/admin-direct-media-provider-job-status?job_id=${encodeURIComponent(jobId)}`,
            isUniversalCompleteMediaJob
              ? `/api/admin-universal-complete-media?job_id=${encodeURIComponent(jobId)}`
              : "",
          ].filter(Boolean)
        : [
            isUniversalCompleteMediaJob
              ? `/api/universal-complete-media-status?job_id=${encodeURIComponent(jobId)}`
              : `/api/universal-complete-media-status?job_id=${encodeURIComponent(jobId)}`,
          ];

    try {
      setStatusMessage(`Checking media job status for ${jobId}...`);

      let lastResult: any = null;
      let lastHttpStatus = 0;

      for (const statusEndpoint of statusEndpoints) {
        const response = await fetch(statusEndpoint, {
          method: "GET",
          headers: {
            "X-Portal-Mode": portalMode,
            "X-Requested-From": "complete_media_popup",
          },
          cache: "no-store",
        });

        lastHttpStatus = response.status;

        const result = await response.json().catch(() => ({
          success: false,
          error: "Invalid JSON response from media job status endpoint.",
          http_status: response.status,
        }));

        lastResult = result;

        const resultStatus = extractPopupMediaStatus(result);
        const resultJobId = extractPopupMediaJobId(result) || jobId;

        const acceptableUniversalStatus =
          isUniversalCompleteMediaJob &&
          [
            "queued",
            "received",
            "running",
            "running_visual_generation",
            "running_audio_generation",
            "running_synchronised_composition",
            "completed",
            "universal_complete_media_visual_failed",
            "universal_complete_media_audio_failed",
            "universal_complete_media_composition_failed",
            "universal_complete_media_exception",
          ].includes(String(resultStatus || result?.status || "").trim());

        const statusRouteSucceeded =
          response.ok &&
          (
            result?.success === true ||
            result?.accepted === true ||
            Boolean(resultStatus) ||
            acceptableUniversalStatus ||
            result?.job_id === jobId ||
            result?.job_id === resultJobId
          );

        if (!statusRouteSucceeded) {
          continue;
        }

        const extracted = applyPopupMediaJobResult({
          ...result,
          job_id: resultJobId,
        });

        const status = extracted.status || resultStatus || result?.status || "status received";

        setStatusMessage(`Media job ${jobId} status: ${status}`);

        const terminalStatus = String(status || "").toLowerCase();
        if (
          terminalStatus === "completed" ||
          terminalStatus.includes("failed") ||
          terminalStatus.includes("exception") ||
          terminalStatus.includes("blocked")
        ) {
          setRunning(false);
        }

        return;
      }

      const fallbackStatus =
        extractPopupMediaStatus(lastResult) ||
        lastResult?.status ||
        "";

      if (isUniversalCompleteMediaJob && fallbackStatus) {
        applyPopupMediaJobResult({
          ...lastResult,
          job_id: jobId,
          status: fallbackStatus,
        });
        setStatusMessage(`Media job ${jobId} status: ${fallbackStatus}`);
        return;
      }

      setStatusMessage(
        lastResult?.error ||
          lastResult?.message ||
          lastResult?.reason ||
          `Media job status check returned HTTP ${lastHttpStatus || 200}, but the response did not match a supported job status shape.`
      );
    } catch (error) {
      setStatusMessage(
        error instanceof Error
          ? error.message
          : "Media job status check failed."
      );
    }
  }

'''

text = text[:start] + new_function + text[end:]

TARGET.write_text(text, encoding="utf-8")

verify = TARGET.read_text(encoding="utf-8")
required = [
    "isUniversalCompleteMediaJob",
    "universal_complete_media_job_",
    "running_visual_generation",
    "running_audio_generation",
    "running_synchronised_composition",
    "statusRouteSucceeded",
    "Media job status check returned HTTP",
]

missing = [item for item in required if item not in verify]
if missing:
    raise SystemExit(f"MISSING_REQUIRED_MARKERS: {missing}")

print("POPUP_UNIVERSAL_MEDIA_STATUS_POLLING_FIXED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {TARGET}")