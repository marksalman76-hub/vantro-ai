from pathlib import Path
from datetime import datetime
import re

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "client" / "page.tsx"
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"client_page_before_compact_real_asset_output_viewer_{timestamp}.tsx"

s = target.read_text(encoding="utf-8")
backup.write_text(s, encoding="utf-8")

compact_viewer = r'''<section className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm">
  <div className="flex items-start justify-between gap-3">
    <div>
      <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">Execution Output Viewer</p>
      <h3 className="mt-1 text-base font-semibold text-slate-950">Real asset preview</h3>
      <p className="mt-1 text-xs text-slate-500">
        Generated assets and runtime deliverables only. No mockups, placeholders, or stock previews.
      </p>
    </div>
    <span className="rounded-full bg-slate-950 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-white">
      Real results
    </span>
  </div>

  <div className="mt-4 rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-4">
    {latestRealAsset ? (
      <div className="flex items-center gap-4">
        <div className="flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          {latestRealAsset.type === "image" && latestRealAsset.url ? (
            <img
              src={latestRealAsset.url}
              alt={latestRealAsset.name || "Generated asset"}
              className="h-full w-full object-cover"
            />
          ) : (
            <div className="px-2 text-center text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400">
              Asset
            </div>
          )}
        </div>

        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-semibold text-slate-950">
            {latestRealAsset.name || latestRealAsset.title || "Generated asset"}
          </p>
          <p className="mt-1 line-clamp-2 text-xs leading-5 text-slate-500">
            {latestRealAsset.summary || latestRealAsset.description || "Real generated asset is ready for review."}
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => setAssetPreviewModalOpen(true)}
              className="rounded-full bg-slate-950 px-3 py-1.5 text-[11px] font-bold text-white shadow-sm transition hover:bg-slate-800"
            >
              Open preview
            </button>
            {latestRealAsset.url ? (
              <a
                href={latestRealAsset.url}
                target="_blank"
                rel="noreferrer"
                className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-[11px] font-bold text-slate-700 transition hover:bg-slate-100"
              >
                Open asset
              </a>
            ) : null}
          </div>
        </div>
      </div>
    ) : (
      <div className="flex min-h-[112px] items-center justify-center rounded-2xl bg-white px-4 text-center">
        <div>
          <p className="text-sm font-semibold text-slate-800">No asset generated yet</p>
          <p className="mt-1 text-xs text-slate-500">
            Real generated or uploaded deliverables will appear here after execution completes.
          </p>
        </div>
      </div>
    )}
  </div>

  <div className="mt-3 grid grid-cols-3 gap-2 text-center">
    <div className="rounded-2xl border border-slate-100 bg-slate-50 px-2 py-2">
      <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400">Source</p>
      <p className="mt-1 truncate text-xs font-semibold text-slate-800">{latestRealAsset ? "Runtime" : "Pending"}</p>
    </div>
    <div className="rounded-2xl border border-slate-100 bg-slate-50 px-2 py-2">
      <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400">Status</p>
      <p className="mt-1 truncate text-xs font-semibold text-slate-800">{latestRealAsset ? "Ready" : "Empty"}</p>
    </div>
    <div className="rounded-2xl border border-slate-100 bg-slate-50 px-2 py-2">
      <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400">Preview</p>
      <p className="mt-1 truncate text-xs font-semibold text-slate-800">{latestRealAsset ? "Modal" : "None"}</p>
    </div>
  </div>

  {assetPreviewModalOpen && latestRealAsset ? (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 p-6">
      <div className="w-full max-w-3xl rounded-3xl bg-white p-5 shadow-2xl">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">Asset preview</p>
            <h3 className="mt-1 text-lg font-semibold text-slate-950">
              {latestRealAsset.name || latestRealAsset.title || "Generated asset"}
            </h3>
          </div>
          <button
            type="button"
            onClick={() => setAssetPreviewModalOpen(false)}
            className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-bold text-slate-700 hover:bg-slate-100"
          >
            Close
          </button>
        </div>

        <div className="mt-4 max-h-[68vh] overflow-auto rounded-2xl border border-slate-200 bg-slate-50 p-4">
          {latestRealAsset.type === "image" && latestRealAsset.url ? (
            <img
              src={latestRealAsset.url}
              alt={latestRealAsset.name || "Generated asset"}
              className="mx-auto max-h-[60vh] rounded-2xl object-contain"
            />
          ) : latestRealAsset.content ? (
            <pre className="whitespace-pre-wrap text-sm leading-6 text-slate-800">{latestRealAsset.content}</pre>
          ) : (
            <p className="text-sm text-slate-500">No previewable content is attached to this asset.</p>
          )}
        </div>
      </div>
    </div>
  ) : null}
</section>'''

# Ensure modal state exists.
if "assetPreviewModalOpen" not in s:
    anchor = re.search(r"(const\s+\[[^\]]+,\s*set[^\]]+\]\s*=\s*useState[^\n]+)", s)
    if anchor:
        insert_at = anchor.end()
        s = s[:insert_at] + "\n  const [assetPreviewModalOpen, setAssetPreviewModalOpen] = useState(false);" + s[insert_at:]
    else:
        raise SystemExit("Could not find a safe useState insertion point.")

# Ensure real asset resolver exists.
if "latestRealAsset" not in s:
    marker = "return ("
    idx = s.find(marker)
    if idx == -1:
        raise SystemExit("Could not find return block.")

    resolver = r'''
  const runtimeAssets =
    Array.isArray((executionResult as any)?.assets)
      ? (executionResult as any).assets
      : Array.isArray((executionResult as any)?.deliverables)
        ? (executionResult as any).deliverables
        : Array.isArray((executionResult as any)?.result?.assets)
          ? (executionResult as any).result.assets
          : [];

  const latestRealAsset =
    runtimeAssets.find((asset: any) =>
      asset &&
      (asset.url || asset.content) &&
      !String(asset.url || "").toLowerCase().includes("placeholder") &&
      !String(asset.url || "").toLowerCase().includes("mock") &&
      !String(asset.name || asset.title || "").toLowerCase().includes("placeholder") &&
      !String(asset.name || asset.title || "").toLowerCase().includes("mock")
    ) || null;

'''
    s = s[:idx] + resolver + s[idx:]

# Replace section containing Execution Output Viewer.
m = re.search(
    r'<section[^>]*>\s*<div[^>]*>[\s\S]{0,1600}?Execution Output Viewer[\s\S]*?</section>',
    s
)
if not m:
    m = re.search(
        r'<div[^>]*>\s*[\s\S]{0,1600}?Execution Output Viewer[\s\S]*?</div>\s*</div>',
        s
    )

if not m:
    raise SystemExit("Could not locate the current Execution Output Viewer block safely.")

s = s[:m.start()] + compact_viewer + s[m.end():]

target.write_text(s, encoding="utf-8")

print("COMPACT_REAL_ASSET_OUTPUT_VIEWER_INSTALLED")
print(f"Backup: {backup}")
print("Updated:", target)