from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"admin_creative_media_assets_frontend_panel_before_{STAMP}"

ADMIN_PAGE = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
API_ROUTE_DIR = ROOT / "frontend" / "src" / "app" / "api" / "admin-creative-media-assets"
API_ROUTE = API_ROUTE_DIR / "route.ts"
TEST_FILE = ROOT / "test_admin_creative_media_assets_frontend_panel.py"

API_ROUTE_CONTENT = r'''import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const BACKEND_BASE_URL =
  process.env.BACKEND_BASE_URL ||
  process.env.NEXT_PUBLIC_BACKEND_BASE_URL ||
  "https://api.trance-formation.com.au";

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_BASE_URL}/admin/creative/media-assets?limit=20`, {
      method: "GET",
      cache: "no-store",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();

    return NextResponse.json(data, {
      status: response.status,
      headers: {
        "Cache-Control": "no-store",
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        layer: "frontend_admin_creative_media_assets_proxy",
        status: "proxy_error",
        error: error instanceof Error ? error.message : String(error),
        credential_values_exposed: false,
      },
      { status: 500 }
    );
  }
}
'''

TEST_CONTENT = r'''from pathlib import Path
import re

ROOT = Path.cwd()

admin_page = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
api_route = ROOT / "frontend" / "src" / "app" / "api" / "admin-creative-media-assets" / "route.ts"

for path in [admin_page, api_route]:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")

admin_text = admin_page.read_text(encoding="utf-8", errors="ignore")
api_text = api_route.read_text(encoding="utf-8", errors="ignore")

required_admin_markers = [
    "Creative Media Assets",
    "admin-creative-media-assets",
    "preview_ready",
    "download_ready",
    "asset_type",
    "provider",
    "local_path",
]

for marker in required_admin_markers:
    if marker not in admin_text:
        raise AssertionError(f"Missing admin marker: {marker}")

required_api_markers = [
    "/admin/creative/media-assets",
    "force-dynamic",
    "no-store",
    "credential_values_exposed",
]

for marker in required_api_markers:
    if marker not in api_text:
        raise AssertionError(f"Missing API marker: {marker}")

if ".env.local" in api_text:
    raise AssertionError("Frontend API route must not reference .env.local")

print("ADMIN_CREATIVE_MEDIA_ASSETS_FRONTEND_PANEL_PASSED")
'''


def backup(path: Path) -> None:
    if path.exists():
        dest = BACKUP / path.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)


def ensure_api_route() -> None:
    backup(API_ROUTE)
    API_ROUTE_DIR.mkdir(parents=True, exist_ok=True)
    API_ROUTE.write_text(API_ROUTE_CONTENT, encoding="utf-8", newline="\n")


def patch_admin_page() -> None:
    if not ADMIN_PAGE.exists():
        raise FileNotFoundError(f"Missing admin page: {ADMIN_PAGE}")

    backup(ADMIN_PAGE)
    text = ADMIN_PAGE.read_text(encoding="utf-8", errors="ignore")

    if "type CreativeMediaAsset" not in text:
        insert_after = '"use client";'
        block = r'''

type CreativeMediaAsset = {
  provider?: string;
  asset_type?: string;
  file_name?: string;
  local_path?: string;
  metadata_path?: string | null;
  size_bytes?: number;
  test_label?: string | null;
  task_id?: string | null;
  status?: string | null;
  preview_ready?: boolean;
  download_ready?: boolean;
  customer_safe?: boolean;
};

type CreativeMediaAssetsResponse = {
  success?: boolean;
  status?: string;
  asset_count?: number;
  total_asset_count?: number;
  assets?: CreativeMediaAsset[];
  credential_values_exposed?: boolean;
};
'''
        text = text.replace(insert_after, insert_after + block, 1)

    if "const [creativeMediaAssets" not in text:
        state_marker = "const ["
        first_state_index = text.find(state_marker)
        if first_state_index == -1:
            raise RuntimeError("Could not find React state location")

        function_start = text.rfind("function", 0, first_state_index)
        if function_start == -1:
            function_start = text.rfind("export default function", 0, first_state_index)

        state_block = r'''
  const [creativeMediaAssets, setCreativeMediaAssets] = useState<CreativeMediaAsset[]>([]);
  const [creativeMediaAssetsLoading, setCreativeMediaAssetsLoading] = useState(false);
  const [creativeMediaAssetsError, setCreativeMediaAssetsError] = useState<string | null>(null);

  async function refreshCreativeMediaAssets() {
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

'''
        text = text[:first_state_index] + state_block + text[first_state_index:]

    if "refreshCreativeMediaAssets();" not in text:
        effect_marker = "useEffect(() => {"
        effect_index = text.find(effect_marker)
        if effect_index != -1:
            close_index = text.find("}, []);", effect_index)
            if close_index != -1:
                text = text[:close_index] + "    refreshCreativeMediaAssets();\n" + text[close_index:]

    panel = r'''
        <section className="rounded-2xl border border-cyan-400/20 bg-slate-950/70 p-5 shadow-lg">
          <div className="mb-4 flex items-center justify-between gap-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-300">Creative Media Assets</p>
              <h2 className="mt-1 text-xl font-bold text-white">Generated audio and video outputs</h2>
              <p className="mt-1 text-sm text-slate-400">
                Latest governed provider assets from ElevenLabs, Runway, Kling, HeyGen and Sync.
              </p>
            </div>
            <button
              type="button"
              onClick={refreshCreativeMediaAssets}
              className="rounded-xl border border-cyan-400/30 px-4 py-2 text-sm font-semibold text-cyan-200 hover:bg-cyan-400/10"
            >
              {creativeMediaAssetsLoading ? "Refreshing..." : "Refresh assets"}
            </button>
          </div>

          {creativeMediaAssetsError ? (
            <div className="rounded-xl border border-red-400/30 bg-red-950/40 p-3 text-sm text-red-200">
              {creativeMediaAssetsError}
            </div>
          ) : null}

          {creativeMediaAssets.length === 0 ? (
            <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-4 text-sm text-slate-400">
              No generated media assets found yet. Run a governed creative media execution to populate this panel.
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {creativeMediaAssets.map((asset, index) => (
                <article
                  key={`${asset.provider}-${asset.file_name}-${index}`}
                  className="rounded-2xl border border-slate-700 bg-slate-900/80 p-4"
                >
                  <div className="mb-3 flex items-center justify-between gap-2">
                    <span className="rounded-full border border-cyan-400/30 bg-cyan-400/10 px-3 py-1 text-xs font-bold uppercase tracking-wide text-cyan-200">
                      {asset.provider || "provider"}
                    </span>
                    <span className="rounded-full border border-purple-400/30 bg-purple-400/10 px-3 py-1 text-xs font-semibold text-purple-200">
                      {asset.asset_type || "asset"}
                    </span>
                  </div>

                  <h3 className="break-words text-sm font-semibold text-white">
                    {asset.test_label || asset.file_name || "Creative media asset"}
                  </h3>

                  <div className="mt-3 space-y-2 text-xs text-slate-400">
                    <p>Status: <span className="text-slate-200">{asset.status || "ready"}</span></p>
                    <p>Preview ready: <span className="text-slate-200">{asset.preview_ready ? "Yes" : "No"}</span></p>
                    <p>Download ready: <span className="text-slate-200">{asset.download_ready ? "Yes" : "No"}</span></p>
                    <p>Size: <span className="text-slate-200">{asset.size_bytes ? `${Math.round(asset.size_bytes / 1024)} KB` : "Unknown"}</span></p>
                  </div>

                  <div className="mt-4 rounded-xl border border-slate-700 bg-slate-950/80 p-3">
                    <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Local file path</p>
                    <p className="break-all text-xs text-slate-300">{asset.local_path || "Not available"}</p>
                  </div>

                  {asset.asset_type === "video" ? (
                    <div className="mt-4 rounded-xl border border-emerald-400/20 bg-emerald-400/5 p-3 text-xs text-emerald-200">
                      Video generated. Use the local path above to open the MP4 until browser-safe streaming is wired.
                    </div>
                  ) : null}

                  {asset.asset_type === "audio" ? (
                    <div className="mt-4 rounded-xl border border-indigo-400/20 bg-indigo-400/5 p-3 text-xs text-indigo-200">
                      Audio generated. Use the local path above to open the MP3 until browser-safe streaming is wired.
                    </div>
                  ) : null}
                </article>
              ))}
            </div>
          )}
        </section>
'''

    if "Creative Media Assets" not in text:
        insertion_markers = [
            "<section",
            "Runtime Health",
            "Provider Governance",
        ]

        inserted = False

        marker = "Runtime Health"
        marker_index = text.find(marker)
        if marker_index != -1:
            section_start = text.rfind("<section", 0, marker_index)
            if section_start != -1:
                text = text[:section_start] + panel + "\n" + text[section_start:]
                inserted = True

        if not inserted:
            main_close = text.rfind("</main>")
            if main_close != -1:
                text = text[:main_close] + panel + "\n" + text[main_close:]
                inserted = True

        if not inserted:
            raise RuntimeError("Could not find insertion point for Creative Media Assets panel")

    ADMIN_PAGE.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    BACKUP.mkdir(parents=True, exist_ok=True)
    ensure_api_route()
    patch_admin_page()
    TEST_FILE.write_text(TEST_CONTENT, encoding="utf-8", newline="\n")

    print("ADMIN_CREATIVE_MEDIA_ASSETS_FRONTEND_PANEL_INSTALLED")
    print(f"Backup folder: {BACKUP}")
    print(f"Updated: {ADMIN_PAGE}")
    print(f"Created/updated: {API_ROUTE}")
    print(f"Created/updated: {TEST_FILE}")


if __name__ == "__main__":
    main()