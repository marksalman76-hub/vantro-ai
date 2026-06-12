from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "frontend" / "src" / "components" / "UniversalCompleteMediaRunAgentPanel.tsx"
BACKUP_DIR = ROOT / "backups" / f"popup_media_job_status_tracker_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if not TARGET.exists():
    raise SystemExit(f"TARGET_NOT_FOUND: {TARGET}")

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP_DIR / TARGET.name)

text = TARGET.read_text(encoding="utf-8")

# Add result state after statusMessage state.
status_state = '''  const [statusMessage, setStatusMessage] = useState(
    "Ready. Click Create complete media now to run directly from this popup."
  );
'''

if status_state not in text:
    raise SystemExit("STATUS_MESSAGE_STATE_BLOCK_NOT_FOUND")

if "popupMediaJobId" not in text:
    text = text.replace(
        status_state,
        status_state + '''
  const [popupMediaJobId, setPopupMediaJobId] = useState("");
  const [popupMediaJobStatus, setPopupMediaJobStatus] = useState("");
  const [popupMediaPreviewUrl, setPopupMediaPreviewUrl] = useState("");
  const [popupMediaAssetUrl, setPopupMediaAssetUrl] = useState("");
  const [popupMediaFinalOutput, setPopupMediaFinalOutput] = useState("");
''',
        1,
    )

# Add helper functions before runCompleteMediaFromPopup.
run_marker = "  async function runCompleteMediaFromPopup() {"
if run_marker not in text:
    raise SystemExit("RUN_FUNCTION_MARKER_NOT_FOUND")

if "async function checkPopupMediaJobStatus" not in text:
    helper = r'''
  function extractPopupMediaJobId(result: any) {
    return (
      result?.media_job_id ||
      result?.job_id ||
      result?.provider_job_id ||
      result?.execution_id ||
      result?.request_id ||
      result?.id ||
      result?.data?.media_job_id ||
      result?.data?.job_id ||
      ""
    );
  }

  function extractPopupMediaUrl(result: any) {
    return (
      result?.preview_url ||
      result?.asset_url ||
      result?.media_url ||
      result?.video_url ||
      result?.audio_url ||
      result?.playable_url ||
      result?.signed_url ||
      result?.final_url ||
      result?.output_url ||
      result?.data?.preview_url ||
      result?.data?.asset_url ||
      result?.data?.media_url ||
      result?.data?.video_url ||
      result?.data?.audio_url ||
      result?.data?.playable_url ||
      result?.data?.signed_url ||
      result?.data?.final_url ||
      result?.data?.output_url ||
      ""
    );
  }

  function extractPopupMediaStatus(result: any) {
    return String(
      result?.media_job_status ||
        result?.job_status ||
        result?.workflow_status ||
        result?.execution_status ||
        result?.status ||
        result?.data?.media_job_status ||
        result?.data?.job_status ||
        result?.data?.status ||
        ""
    );
  }

  function extractPopupFinalOutput(result: any) {
    const value =
      result?.final_output ||
      result?.output ||
      result?.result ||
      result?.message ||
      result?.data?.final_output ||
      result?.data?.output ||
      result?.data?.result ||
      result?.data?.message ||
      "";

    if (!value) return "";

    if (typeof value === "string") return value;

    try {
      return JSON.stringify(value, null, 2);
    } catch {
      return String(value);
    }
  }

  function applyPopupMediaJobResult(result: any) {
    const jobId = extractPopupMediaJobId(result);
    const status = extractPopupMediaStatus(result);
    const url = extractPopupMediaUrl(result);
    const finalOutput = extractPopupFinalOutput(result);

    if (jobId) setPopupMediaJobId(jobId);
    if (status) setPopupMediaJobStatus(status);
    if (url) {
      setPopupMediaPreviewUrl(url);
      setPopupMediaAssetUrl(url);
    }
    if (finalOutput) setPopupMediaFinalOutput(finalOutput);

    return { jobId, status, url, finalOutput };
  }

  async function checkPopupMediaJobStatus(jobIdOverride?: string) {
    const jobId = jobIdOverride || popupMediaJobId;

    if (!jobId) {
      setStatusMessage("No media job ID is available yet.");
      return;
    }

    const statusEndpoint =
      portalMode === "admin"
        ? `/api/admin-direct-media-provider-job-status?job_id=${encodeURIComponent(jobId)}`
        : `/api/universal-complete-media-status?job_id=${encodeURIComponent(jobId)}`;

    try {
      setStatusMessage(`Checking media job status for ${jobId}...`);

      const response = await fetch(statusEndpoint, {
        method: "GET",
        headers: {
          "X-Portal-Mode": portalMode,
          "X-Requested-From": "complete_media_popup",
        },
      });

      const result = await response.json().catch(() => ({
        success: false,
        error: "Invalid JSON response from media job status endpoint.",
      }));

      if (!response.ok || result?.success === false) {
        setStatusMessage(
          result?.error ||
            result?.message ||
            `Media job status check failed with HTTP ${response.status}.`
        );
        return;
      }

      const extracted = applyPopupMediaJobResult(result);

      setStatusMessage(
        extracted.status
          ? `Media job ${jobId} status: ${extracted.status}`
          : `Media job ${jobId} status received.`
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
    text = text.replace(run_marker, helper + run_marker, 1)

# After successful result, apply job result and immediately check status.
success_marker = '''      const jobId =
        result?.media_job_id ||
        result?.job_id ||
        result?.provider_job_id ||
        result?.execution_id ||
        result?.request_id ||
        result?.id ||
        "";'''

if success_marker not in text:
    raise SystemExit("SUCCESS_JOB_ID_MARKER_NOT_FOUND")

new_success_marker = '''      const extractedPopupResult = applyPopupMediaJobResult(result);

      const jobId =
        extractedPopupResult.jobId ||
        result?.media_job_id ||
        result?.job_id ||
        result?.provider_job_id ||
        result?.execution_id ||
        result?.request_id ||
        result?.id ||
        "";'''

text = text.replace(success_marker, new_success_marker, 1)

status_marker = '''      onResult?.(result);'''

if status_marker not in text:
    raise SystemExit("ONRESULT_MARKER_NOT_FOUND")

if "checkPopupMediaJobStatus(jobId);" not in text:
    text = text.replace(
        status_marker,
        '''      if (jobId) {
        setTimeout(() => {
          void checkPopupMediaJobStatus(jobId);
        }, 1200);
      }

''' + status_marker,
        1,
    )

# Add visible result tracker after status message box.
status_box_marker = '''              <div
                data-complete-media-popup-status="true"'''

status_box_start = text.find(status_box_marker)
if status_box_start == -1:
    raise SystemExit("STATUS_BOX_START_NOT_FOUND")

status_box_end = text.find("              </div>", status_box_start)
if status_box_end == -1:
    raise SystemExit("STATUS_BOX_END_NOT_FOUND")

status_box_end += len("              </div>")

if "data-complete-media-popup-result-tracker" not in text:
    tracker = r'''

              <div
                data-complete-media-popup-result-tracker="true"
                style={{
                  display: popupMediaJobId || popupMediaPreviewUrl || popupMediaFinalOutput ? "grid" : "none",
                  gap: 10,
                  borderRadius: 16,
                  padding: 12,
                  border: "1px solid rgba(34,197,94,.24)",
                  background:
                    portalMode === "admin"
                      ? "rgba(15,23,42,.48)"
                      : "rgba(240,253,244,.8)",
                  color: portalMode === "admin" ? "#d1fae5" : "#14532d",
                  fontSize: 12.5,
                  lineHeight: 1.55,
                }}
              >
                <div style={{ fontWeight: 950 }}>Media job result</div>

                {popupMediaJobId ? (
                  <div>
                    <strong>Job ID:</strong> {popupMediaJobId}
                  </div>
                ) : null}

                {popupMediaJobStatus ? (
                  <div>
                    <strong>Status:</strong> {popupMediaJobStatus}
                  </div>
                ) : null}

                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  {popupMediaJobId ? (
                    <button
                      type="button"
                      onClick={() => void checkPopupMediaJobStatus()}
                      style={{
                        width: "fit-content",
                        border: "1px solid rgba(34,197,94,.32)",
                        borderRadius: 999,
                        padding: "8px 12px",
                        background:
                          portalMode === "admin"
                            ? "rgba(34,197,94,.13)"
                            : "#fff",
                        color: portalMode === "admin" ? "#bbf7d0" : "#166534",
                        fontWeight: 900,
                        cursor: "pointer",
                      }}
                    >
                      Refresh media status
                    </button>
                  ) : null}

                  {popupMediaAssetUrl ? (
                    <a
                      href={popupMediaAssetUrl}
                      target="_blank"
                      rel="noreferrer"
                      style={{
                        width: "fit-content",
                        border: "1px solid rgba(59,130,246,.32)",
                        borderRadius: 999,
                        padding: "8px 12px",
                        color: portalMode === "admin" ? "#bfdbfe" : "#1d4ed8",
                        textDecoration: "none",
                        fontWeight: 900,
                      }}
                    >
                      Open media asset
                    </a>
                  ) : null}
                </div>

                {popupMediaPreviewUrl ? (
                  popupMediaPreviewUrl.match(/\.(mp4|webm|mov)(\?|$)/i) ? (
                    <video
                      src={popupMediaPreviewUrl}
                      controls
                      style={{
                        width: "100%",
                        maxHeight: 360,
                        borderRadius: 14,
                        background: "#020617",
                      }}
                    />
                  ) : popupMediaPreviewUrl.match(/\.(mp3|wav|m4a|ogg)(\?|$)/i) ? (
                    <audio src={popupMediaPreviewUrl} controls style={{ width: "100%" }} />
                  ) : popupMediaPreviewUrl.match(/\.(png|jpg|jpeg|webp|gif)(\?|$)/i) ? (
                    <img
                      src={popupMediaPreviewUrl}
                      alt="Generated media preview"
                      style={{
                        width: "100%",
                        maxHeight: 360,
                        objectFit: "contain",
                        borderRadius: 14,
                        background: "#020617",
                      }}
                    />
                  ) : (
                    <div>
                      <strong>Preview URL:</strong> {popupMediaPreviewUrl}
                    </div>
                  )
                ) : null}

                {popupMediaFinalOutput ? (
                  <pre
                    style={{
                      whiteSpace: "pre-wrap",
                      overflow: "auto",
                      maxHeight: 220,
                      borderRadius: 14,
                      padding: 10,
                      background:
                        portalMode === "admin"
                          ? "rgba(2,6,23,.78)"
                          : "rgba(255,255,255,.78)",
                      color: portalMode === "admin" ? "#e5e7eb" : "#0f172a",
                    }}
                  >
                    {popupMediaFinalOutput}
                  </pre>
                ) : null}
              </div>'''
    text = text[:status_box_end] + tracker + text[status_box_end:]

TARGET.write_text(text, encoding="utf-8")

verify = TARGET.read_text(encoding="utf-8")
required = [
    "popupMediaJobId",
    "checkPopupMediaJobStatus",
    "data-complete-media-popup-result-tracker",
    "Refresh media status",
    "Open media asset",
    "/api/admin-direct-media-provider-job-status",
    "/api/universal-complete-media-status",
]

missing = [item for item in required if item not in verify]
if missing:
    raise SystemExit(f"MISSING_REQUIRED_MARKERS: {missing}")

print("POPUP_MEDIA_JOB_STATUS_TRACKER_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {TARGET}")