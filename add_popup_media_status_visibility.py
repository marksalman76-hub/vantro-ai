from pathlib import Path
from datetime import datetime

p = Path("frontend/src/app/admin/page.tsx")
s = p.read_text(encoding="utf-8")

backup_dir = Path("backups") / f"popup_media_status_visibility_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
(backup_dir / "page.tsx").write_text(s, encoding="utf-8")

def replace_once(source: str, old: str, new: str) -> str:
    if old not in source:
        raise SystemExit(f"Could not find expected block:\n{old[:500]}")
    return source.replace(old, new, 1)

# 1) Add a richer popup media job status type after CreativeMediaAssetsResponse.
old = """type CreativeMediaAssetsResponse = {
  success?: boolean;
  status?: string;
  asset_count?: number;
  total_asset_count?: number;
  assets?: CreativeMediaAsset[];
  credential_values_exposed?: boolean;
};
"""

new = """type CreativeMediaAssetsResponse = {
  success?: boolean;
  status?: string;
  asset_count?: number;
  total_asset_count?: number;
  assets?: CreativeMediaAsset[];
  credential_values_exposed?: boolean;
};

type PopupMediaJobStatus = {
  job_id: string;
  status: string;
  message?: string;
  provider?: string;
  created_at?: string;
  updated_at?: string;
  raw_result?: any;
  matched_assets?: CreativeMediaAsset[];
};
"""

s = replace_once(s, old, new)

# 2) Add helper functions after Panel().
old = """function Panel({ title, subtitle, children }: { title: string; subtitle?: string; children: React.ReactNode }) {
  return (
    <div className="panel">
      <h2>{title}</h2>
      {subtitle ? <p>{subtitle}</p> : null}
      {children}
    </div>
  );
}
"""

new = """function Panel({ title, subtitle, children }: { title: string; subtitle?: string; children: React.ReactNode }) {
  return (
    <div className="panel">
      <h2>{title}</h2>
      {subtitle ? <p>{subtitle}</p> : null}
      {children}
    </div>
  );
}

function normaliseMediaStatus(value: any): string {
  const text = String(value || "").toLowerCase();
  if (!text) return "queued";
  if (text.includes("fail") || text.includes("error") || text.includes("blocked")) return "failed";
  if (text.includes("complete") || text.includes("ready") || text.includes("success") || text.includes("delivered")) return "completed";
  if (text.includes("process") || text.includes("poll") || text.includes("running") || text.includes("provider")) return "processing";
  if (text.includes("queue") || text.includes("submit") || text.includes("accept") || text.includes("created")) return "queued";
  return text.replaceAll("_", " ");
}

function extractMediaJobIdFromResult(result: any): string {
  return String(
    result?.media_job_id ||
      result?.job_id ||
      result?.canonical_job_id ||
      result?.media_job?.job_id ||
      result?.data?.media_job_id ||
      result?.data?.job_id ||
      result?.data?.media_job?.job_id ||
      result?.creative_payload?.media_job_id ||
      result?.output?.media_job_id ||
      result?.execution?.media_job_id ||
      result?.execution?.adapter_result?.media_job_id ||
      result?.execution?.adapter_result?.creative_media_pack?.media_job_id ||
      result?.execution?.adapter_result?.asset?.media_job_id ||
      ""
  ).trim();
}

function assetMatchesMediaJob(asset: CreativeMediaAsset, jobId: string): boolean {
  const needle = String(jobId || "").trim();
  if (!needle) return false;

  return [
    asset.job_id,
    asset.media_job_id,
    asset.task_id,
    asset.metadata_path,
    asset.local_path,
    asset.file_name,
  ]
    .map((value) => String(value || ""))
    .some((value) => value.includes(needle));
}

function summarisePopupMediaStatus(job: PopupMediaJobStatus | null): string {
  if (!job?.job_id) return "No popup media job submitted yet.";
  const assets = Array.isArray(job.matched_assets) ? job.matched_assets : [];
  if (assets.some((asset) => asset.playable || asset.signed_delivery_created || asset.preview_ready || asset.download_ready)) {
    return "completed";
  }
  if (assets.length > 0) {
    return normaliseMediaStatus(assets[0]?.status || assets[0]?.delivery_status || job.status);
  }
  return normaliseMediaStatus(job.status);
}
"""

s = replace_once(s, old, new)

# 3) Add popup job state after existing creativeMediaAssets state.
old = """  const [creativeMediaAssets, setCreativeMediaAssets] = useState<CreativeMediaAsset[]>([]);
  const [creativeMediaAssetsLoading, setCreativeMediaAssetsLoading] = useState(false);
  const [creativeMediaAssetsError, setCreativeMediaAssetsError] = useState<string | null>(null);
"""

new = """  const [creativeMediaAssets, setCreativeMediaAssets] = useState<CreativeMediaAsset[]>([]);
  const [creativeMediaAssetsLoading, setCreativeMediaAssetsLoading] = useState(false);
  const [creativeMediaAssetsError, setCreativeMediaAssetsError] = useState<string | null>(null);
  const [popupMediaJobStatus, setPopupMediaJobStatus] = useState<PopupMediaJobStatus | null>(null);
  const [popupMediaPolling, setPopupMediaPolling] = useState(false);
"""

s = replace_once(s, old, new)

# 4) Add a helper to refresh and match assets after refreshCreativeMediaAssets().
old = """  async function refreshCreativeMediaAssets() {
    setCreativeMediaAssetsLoading(true);
    setCreativeMediaAssetsError(null);

    try {
      const response = await fetch("/api/admin-creative-media-assets", {
        method: "GET",
        cache: "no-store",
      });

      const data: CreativeMediaAssetsResponse = await response.json();

      if (!response.ok || data?.success === false) {
        throw new Error(data?.status || "Unable to load creative media assets");
      }

      setCreativeMediaAssets(Array.isArray(data.assets) ? data.assets : []);
    } catch (error) {
      setCreativeMediaAssetsError(error instanceof Error ? error.message : String(error));
    } finally {
      setCreativeMediaAssetsLoading(false);
    }
  }
"""

new = """  async function refreshCreativeMediaAssets() {
    setCreativeMediaAssetsLoading(true);
    setCreativeMediaAssetsError(null);

    try {
      const response = await fetch("/api/admin-creative-media-assets", {
        method: "GET",
        cache: "no-store",
      });

      const data: CreativeMediaAssetsResponse = await response.json();

      if (!response.ok || data?.success === false) {
        throw new Error(data?.status || "Unable to load creative media assets");
      }

      setCreativeMediaAssets(Array.isArray(data.assets) ? data.assets : []);
    } catch (error) {
      setCreativeMediaAssetsError(error instanceof Error ? error.message : String(error));
    } finally {
      setCreativeMediaAssetsLoading(false);
    }
  }

  async function refreshPopupMediaJobStatus(jobId: string, baseStatus?: PopupMediaJobStatus | null) {
    const cleanJobId = String(jobId || "").trim();
    if (!cleanJobId) return;

    setPopupMediaPolling(true);

    try {
      const response = await fetch("/api/admin-creative-media-assets", {
        method: "GET",
        cache: "no-store",
      });

      const data: CreativeMediaAssetsResponse = await response.json();

      if (!response.ok || data?.success === false) {
        throw new Error(data?.status || "Unable to load creative media assets");
      }

      const assets = Array.isArray(data.assets) ? data.assets : [];
      setCreativeMediaAssets(assets);

      const matchedAssets = assets.filter((asset) => assetMatchesMediaJob(asset, cleanJobId));
      const firstAsset = matchedAssets[0];

      setPopupMediaJobStatus((previous) => {
        const seed = baseStatus || previous || {
          job_id: cleanJobId,
          status: "queued",
        };

        return {
          ...seed,
          job_id: cleanJobId,
          status: normaliseMediaStatus(
            firstAsset?.delivery_status ||
              firstAsset?.status ||
              seed.status ||
              "queued"
          ),
          message:
            matchedAssets.length > 0
              ? `${matchedAssets.length} generated asset record(s) matched this popup media job.`
              : seed.message || "Media job accepted. Waiting for generated asset records.",
          provider: firstAsset?.provider || seed.provider,
          matched_assets: matchedAssets,
          updated_at: new Date().toISOString(),
        };
      });
    } catch (error) {
      setPopupMediaJobStatus((previous) => ({
        ...(baseStatus || previous || { job_id: cleanJobId }),
        job_id: cleanJobId,
        status: previous?.status || baseStatus?.status || "queued",
        message: error instanceof Error ? error.message : String(error),
        updated_at: new Date().toISOString(),
      }));
    } finally {
      setPopupMediaPolling(false);
    }
  }
"""

s = replace_once(s, old, new)

# 5) Add polling effect before navItems.
old = """  const navItems = ["Overview", "Run Agent", "Deploy Clients", "Client Registry", "Runtime Health", "Provider Governance", "Orchestration", "Recovery", "Billing", "Operations Store"];
"""

new = """  useEffect(() => {
    const jobId = popupMediaJobStatus?.job_id;
    const status = summarisePopupMediaStatus(popupMediaJobStatus);

    if (!jobId || ["completed", "failed"].includes(status)) {
      return;
    }

    const timer = window.setInterval(() => {
      refreshPopupMediaJobStatus(jobId);
    }, 6000);

    return () => window.clearInterval(timer);
  }, [popupMediaJobStatus?.job_id, popupMediaJobStatus?.status, popupMediaJobStatus?.matched_assets?.length]);

  const navItems = ["Overview", "Run Agent", "Deploy Clients", "Client Registry", "Runtime Health", "Provider Governance", "Orchestration", "Recovery", "Billing", "Operations Store"];
"""

s = replace_once(s, old, new)

# 6) Capture the media job id from popup result and start status tracking.
old = """        const wrapper = await response.json();
        const result = wrapper?.data || wrapper;

        setRunResult({
          ...result,
          success: response.ok && result?.success !== false,
          status: result?.status || result?.message || "complete_media_workflow_submitted",
"""

new = """        const wrapper = await response.json();
        const result = wrapper?.data || wrapper;
        const popupMediaJobId = extractMediaJobIdFromResult(result);

        if (popupMediaJobId) {
          const initialPopupMediaStatus: PopupMediaJobStatus = {
            job_id: popupMediaJobId,
            status: normaliseMediaStatus(result?.status || result?.message || "queued"),
            message: result?.message || result?.status || "Complete media workflow submitted.",
            provider: result?.provider || result?.provider_key || "universal_complete_media",
            raw_result: result,
            matched_assets: [],
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          };

          setPopupMediaJobStatus(initialPopupMediaStatus);
          refreshPopupMediaJobStatus(popupMediaJobId, initialPopupMediaStatus);
        } else {
          setPopupMediaJobStatus({
            job_id: "",
            status: normaliseMediaStatus(result?.status || result?.message || "submitted"),
            message: "Complete media workflow submitted, but no media job ID was returned yet.",
            provider: result?.provider || result?.provider_key || "universal_complete_media",
            raw_result: result,
            matched_assets: [],
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          });
        }

        setRunResult({
          ...result,
          media_job_id: popupMediaJobId || result?.media_job_id || result?.job_id || null,
          success: response.ok && result?.success !== false,
          status: result?.status || result?.message || "complete_media_workflow_submitted",
"""

s = replace_once(s, old, new)

# 7) Clear status on popup failure.
old = """      } catch {
        showToast("Admin complete media workflow failed before reaching backend.");
        setRunResult({
"""

new = """      } catch {
        showToast("Admin complete media workflow failed before reaching backend.");
        setPopupMediaJobStatus({
          job_id: "",
          status: "failed",
          message: "Admin complete media workflow failed before reaching backend.",
          provider: "universal_complete_media",
          matched_assets: [],
          updated_at: new Date().toISOString(),
        });
        setRunResult({
"""

s = replace_once(s, old, new)

# 8) Insert the status/result visibility panel under the Run button before run output.
old = """              <button className="primary" onClick={runAdminAgentWithMediaOptions} disabled={running}>{running ? "Running..." : selectedRun.length > 1 ? "Run Selected Agents" : "Run Agent"}</button>

              <div className={runResult ? "output has premiumExecutionOutput" : "output premiumExecutionOutput"}>
"""

new = """              <button className="primary" onClick={runAdminAgentWithMediaOptions} disabled={running}>{running ? "Running..." : selectedRun.length > 1 ? "Run Selected Agents" : "Run Agent"}</button>

              {popupMediaJobStatus ? (
                <div className="popupMediaStatusPanel">
                  <div className="popupMediaStatusHeader">
                    <div>
                      <small>CREATE MEDIA JOB STATUS</small>
                      <strong>{summarisePopupMediaStatus(popupMediaJobStatus)}</strong>
                      <p>{popupMediaJobStatus.message || "Waiting for media job status."}</p>
                    </div>
                    <button
                      className="ghost"
                      type="button"
                      disabled={!popupMediaJobStatus.job_id || popupMediaPolling}
                      onClick={() => refreshPopupMediaJobStatus(popupMediaJobStatus.job_id)}
                    >
                      {popupMediaPolling ? "Checking..." : "Check status"}
                    </button>
                  </div>

                  <div className="popupMediaStatusGrid">
                    <div>
                      <small>Job ID</small>
                      <span>{popupMediaJobStatus.job_id || "Pending job ID"}</span>
                    </div>
                    <div>
                      <small>Provider</small>
                      <span>{popupMediaJobStatus.provider || "universal_complete_media"}</span>
                    </div>
                    <div>
                      <small>Assets matched</small>
                      <span>{popupMediaJobStatus.matched_assets?.length || 0}</span>
                    </div>
                    <div>
                      <small>Updated</small>
                      <span>{popupMediaJobStatus.updated_at ? new Date(popupMediaJobStatus.updated_at).toLocaleTimeString() : "Waiting"}</span>
                    </div>
                  </div>

                  {popupMediaJobStatus.matched_assets && popupMediaJobStatus.matched_assets.length > 0 ? (
                    <div className="popupMediaAssetList">
                      {popupMediaJobStatus.matched_assets.slice(0, 4).map((asset, index) => (
                        <div className="popupMediaAssetCard" key={`${asset.job_id || asset.media_job_id || asset.task_id || index}`}>
                          <div>
                            <strong>{asset.test_label || asset.file_name || asset.asset_type || "Generated media asset"}</strong>
                            <p>Status: {asset.delivery_status || asset.status || "ready"}</p>
                            <p>Preview: {asset.preview_ready ? "ready" : "not ready"} · Download: {asset.download_ready ? "ready" : "not ready"} · Playable: {asset.playable ? "yes" : "no"}</p>
                            {asset.local_path ? <p className="breakText">File: {asset.local_path}</p> : null}
                            {asset.blocked_reason || asset.not_playable_reason ? (
                              <p className="warningText">{asset.blocked_reason || asset.not_playable_reason}</p>
                            ) : null}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="popupMediaWaiting">
                      Job accepted. The popup will keep checking for queued, processing, completed, failed, and asset-ready status.
                    </div>
                  )}
                </div>
              ) : null}

              <div className={runResult ? "output has premiumExecutionOutput" : "output premiumExecutionOutput"}>
"""

s = replace_once(s, old, new)

# 9) Add CSS before existing .premiumExecutionOutput style.
old = """        .premiumExecutionOutput{min-height:150px}
"""

new = """        .popupMediaStatusPanel{margin-top:14px;border:1px solid rgba(14,207,188,.2);background:rgba(14,207,188,.045);border-radius:16px;padding:16px;color:#cbd5e1}
        .popupMediaStatusHeader{display:flex;justify-content:space-between;gap:16px;align-items:flex-start}
        .popupMediaStatusHeader small{display:block;color:#67e8f9;font-size:10px;font-weight:950;letter-spacing:.14em}
        .popupMediaStatusHeader strong{display:block;color:#fff;text-transform:uppercase;font-size:18px;margin-top:4px}
        .popupMediaStatusHeader p{margin:6px 0 0;color:#a8b3cf;font-size:13px;line-height:1.45}
        .popupMediaStatusGrid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:14px}
        .popupMediaStatusGrid div{border:1px solid rgba(255,255,255,.08);background:rgba(2,6,23,.55);border-radius:12px;padding:10px;min-width:0}
        .popupMediaStatusGrid small{display:block;color:#94a3b8;font-size:10px;text-transform:uppercase;letter-spacing:.12em}
        .popupMediaStatusGrid span{display:block;color:#e2e8f0;font-size:12px;font-weight:850;margin-top:5px;word-break:break-word}
        .popupMediaAssetList{display:grid;grid-template-columns:1fr;gap:10px;margin-top:14px}
        .popupMediaAssetCard{border:1px solid rgba(16,185,129,.18);background:rgba(16,185,129,.055);border-radius:12px;padding:12px}
        .popupMediaAssetCard strong{display:block;color:#f8fafc}
        .popupMediaAssetCard p{margin:5px 0 0;color:#cbd5e1;font-size:12px}
        .popupMediaWaiting{margin-top:14px;border:1px dashed rgba(148,163,184,.22);border-radius:12px;padding:12px;color:#a8b3cf;font-size:13px;background:rgba(2,6,23,.35)}
        .breakText{word-break:break-all}
        .warningText{color:#fcd34d!important}
        .premiumExecutionOutput{min-height:150px}
"""

s = replace_once(s, old, new)

p.write_text(s, encoding="utf-8")
print("POPUP_MEDIA_STATUS_VISIBILITY_ADDED")
print(f"Updated: {p}")
print(f"Backup: {backup_dir}")