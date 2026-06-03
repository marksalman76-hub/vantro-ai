from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "backups" / f"admin_creative_assets_standalone_page_before_{STAMP}"

PAGE_DIR = ROOT / "frontend" / "src" / "app" / "admin" / "creative-assets"
PAGE_FILE = PAGE_DIR / "page.tsx"

API_DIR = ROOT / "frontend" / "src" / "app" / "api" / "admin-creative-media-assets"
API_FILE = API_DIR / "route.ts"

TEST_FILE = ROOT / "test_admin_creative_assets_standalone_page.py"

PAGE_CONTENT = r'''"use client";

import { useEffect, useState } from "react";

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

type CreativeAssetsResponse = {
  success?: boolean;
  asset_count?: number;
  total_asset_count?: number;
  assets?: CreativeMediaAsset[];
  providers_checked?: string[];
  credential_values_exposed?: boolean;
  status?: string;
  error?: string;
};

export const dynamic = "force-dynamic";

export default function AdminCreativeAssetsPage() {
  const [assets, setAssets] = useState<CreativeMediaAsset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [meta, setMeta] = useState<CreativeAssetsResponse | null>(null);

  async function loadAssets() {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/admin-creative-media-assets", {
        method: "GET",
        cache: "no-store",
      });

      const data: CreativeAssetsResponse = await response.json();

      if (!response.ok || data.success === false) {
        throw new Error(data.error || data.status || "Unable to load creative assets");
      }

      setAssets(Array.isArray(data.assets) ? data.assets : []);
      setMeta(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAssets();
  }, []);

  return (
    <main style={{
      minHeight: "100vh",
      background: "#050816",
      color: "#e5e7eb",
      padding: "32px",
      fontFamily: "Inter, Arial, sans-serif"
    }}>
      <div style={{maxWidth: "1280px", margin: "0 auto"}}>
        <div style={{display: "flex", justifyContent: "space-between", gap: "16px", alignItems: "center", marginBottom: "28px"}}>
          <div>
            <p style={{color: "#22d3ee", fontWeight: 900, fontSize: "12px", letterSpacing: ".2em", textTransform: "uppercase"}}>
              Owner Command Centre
            </p>
            <h1 style={{fontSize: "34px", lineHeight: 1.1, marginTop: "8px", color: "white"}}>
              Creative Media Assets
            </h1>
            <p style={{color: "#94a3b8", marginTop: "8px"}}>
              Generated audio and video outputs from ElevenLabs, Runway, Kling, HeyGen and Sync.
            </p>
          </div>

          <div style={{display: "flex", gap: "10px"}}>
            <a
              href="/admin"
              style={{
                color: "#c4b5fd",
                border: "1px solid rgba(196,181,253,.35)",
                borderRadius: "12px",
                padding: "10px 14px",
                textDecoration: "none",
                fontWeight: 800
              }}
            >
              Back to Admin
            </a>
            <button
              onClick={loadAssets}
              style={{
                color: "#a5f3fc",
                background: "rgba(8,145,178,.15)",
                border: "1px solid rgba(34,211,238,.4)",
                borderRadius: "12px",
                padding: "10px 14px",
                fontWeight: 900,
                cursor: "pointer"
              }}
            >
              {loading ? "Refreshing..." : "Refresh assets"}
            </button>
          </div>
        </div>

        <section style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))",
          gap: "14px",
          marginBottom: "24px"
        }}>
          <Metric label="Asset count" value={String(meta?.asset_count ?? assets.length)} />
          <Metric label="Total detected" value={String(meta?.total_asset_count ?? assets.length)} />
          <Metric label="Credential safe" value={meta?.credential_values_exposed === false ? "Yes" : "Check"} />
          <Metric label="Providers" value={(meta?.providers_checked || []).length ? String((meta?.providers_checked || []).length) : "5"} />
        </section>

        {error ? (
          <section style={{
            border: "1px solid rgba(248,113,113,.35)",
            background: "rgba(127,29,29,.25)",
            borderRadius: "16px",
            padding: "16px",
            color: "#fecaca",
            marginBottom: "20px"
          }}>
            {error}
          </section>
        ) : null}

        {loading ? (
          <section style={{
            border: "1px solid rgba(148,163,184,.2)",
            background: "rgba(15,23,42,.7)",
            borderRadius: "18px",
            padding: "22px",
            color: "#cbd5e1"
          }}>
            Loading generated media assets...
          </section>
        ) : assets.length === 0 ? (
          <section style={{
            border: "1px solid rgba(148,163,184,.2)",
            background: "rgba(15,23,42,.7)",
            borderRadius: "18px",
            padding: "22px",
            color: "#cbd5e1"
          }}>
            No generated media assets found yet. Run a governed UGC creative media execution, then refresh this page.
          </section>
        ) : (
          <section style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit,minmax(320px,1fr))",
            gap: "18px"
          }}>
            {assets.map((asset, index) => (
              <article
                key={`${asset.provider}-${asset.file_name}-${index}`}
                style={{
                  border: "1px solid rgba(148,163,184,.22)",
                  background: "rgba(15,23,42,.82)",
                  borderRadius: "18px",
                  padding: "18px",
                  boxShadow: "0 18px 48px rgba(0,0,0,.28)"
                }}
              >
                <div style={{display: "flex", justifyContent: "space-between", gap: "10px", marginBottom: "12px"}}>
                  <span style={{
                    color: "#67e8f9",
                    background: "rgba(8,145,178,.12)",
                    border: "1px solid rgba(34,211,238,.32)",
                    borderRadius: "999px",
                    padding: "6px 10px",
                    fontSize: "12px",
                    fontWeight: 900,
                    textTransform: "uppercase"
                  }}>
                    {asset.provider || "provider"}
                  </span>
                  <span style={{
                    color: "#c4b5fd",
                    background: "rgba(124,58,237,.12)",
                    border: "1px solid rgba(196,181,253,.25)",
                    borderRadius: "999px",
                    padding: "6px 10px",
                    fontSize: "12px",
                    fontWeight: 900,
                    textTransform: "uppercase"
                  }}>
                    {asset.asset_type || "asset"}
                  </span>
                </div>

                <h2 style={{fontSize: "16px", color: "white", wordBreak: "break-word"}}>
                  {asset.test_label || asset.file_name || "Creative media asset"}
                </h2>

                <div style={{marginTop: "14px", display: "grid", gap: "8px", color: "#cbd5e1", fontSize: "13px"}}>
                  <p>Status: <strong style={{color: "white"}}>{asset.status || "ready"}</strong></p>
                  <p>Preview ready: <strong style={{color: "white"}}>{asset.preview_ready ? "Yes" : "No"}</strong></p>
                  <p>Download ready: <strong style={{color: "white"}}>{asset.download_ready ? "Yes" : "No"}</strong></p>
                  <p>Size: <strong style={{color: "white"}}>{asset.size_bytes ? `${Math.round(asset.size_bytes / 1024)} KB` : "Unknown"}</strong></p>
                </div>

                <div style={{
                  marginTop: "14px",
                  border: "1px solid rgba(148,163,184,.18)",
                  background: "rgba(2,6,23,.65)",
                  borderRadius: "12px",
                  padding: "12px"
                }}>
                  <p style={{fontSize: "11px", color: "#64748b", textTransform: "uppercase", fontWeight: 900, marginBottom: "8px"}}>
                    Local file path
                  </p>
                  <p style={{fontSize: "12px", color: "#e2e8f0", wordBreak: "break-all"}}>
                    {asset.local_path || "Not available"}
                  </p>
                </div>

                {asset.metadata_path ? (
                  <div style={{
                    marginTop: "10px",
                    border: "1px solid rgba(148,163,184,.12)",
                    borderRadius: "12px",
                    padding: "10px"
                  }}>
                    <p style={{fontSize: "11px", color: "#64748b", textTransform: "uppercase", fontWeight: 900, marginBottom: "8px"}}>
                      Metadata path
                    </p>
                    <p style={{fontSize: "11px", color: "#94a3b8", wordBreak: "break-all"}}>
                      {asset.metadata_path}
                    </p>
                  </div>
                ) : null}
              </article>
            ))}
          </section>
        )}
      </div>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div style={{
      border: "1px solid rgba(148,163,184,.2)",
      background: "rgba(15,23,42,.72)",
      borderRadius: "16px",
      padding: "16px"
    }}>
      <p style={{fontSize: "11px", color: "#64748b", textTransform: "uppercase", fontWeight: 900, letterSpacing: ".12em"}}>
        {label}
      </p>
      <p style={{fontSize: "26px", color: "white", fontWeight: 950, marginTop: "6px"}}>
        {value}
      </p>
    </div>
  );
}
'''

API_CONTENT = r'''import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const BACKEND_BASE_URL =
  process.env.BACKEND_BASE_URL ||
  process.env.NEXT_PUBLIC_BACKEND_BASE_URL ||
  "https://api.trance-formation.com.au";

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_BASE_URL}/admin/creative/media-assets?limit=50`, {
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

ROOT = Path.cwd()
page = ROOT / "frontend" / "src" / "app" / "admin" / "creative-assets" / "page.tsx"
api = ROOT / "frontend" / "src" / "app" / "api" / "admin-creative-media-assets" / "route.ts"

for path in [page, api]:
    if not path.exists():
        raise AssertionError(f"Missing: {path}")

page_text = page.read_text(encoding="utf-8", errors="ignore")
api_text = api.read_text(encoding="utf-8", errors="ignore")

for marker in [
    "Creative Media Assets",
    "Generated audio and video outputs",
    "Refresh assets",
    "Local file path",
    "Back to Admin",
]:
    if marker not in page_text:
        raise AssertionError(f"Missing page marker: {marker}")

for marker in [
    "/admin/creative/media-assets",
    "force-dynamic",
    "no-store",
    "credential_values_exposed",
]:
    if marker not in api_text:
        raise AssertionError(f"Missing API marker: {marker}")

print("ADMIN_CREATIVE_ASSETS_STANDALONE_PAGE_PASSED")
'''

def backup(path: Path):
    if path.exists():
        dest = BACKUP / path.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)

def write(path: Path, content: str):
    backup(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")

def main():
    BACKUP.mkdir(parents=True, exist_ok=True)
    write(PAGE_FILE, PAGE_CONTENT)
    write(API_FILE, API_CONTENT)
    write(TEST_FILE, TEST_CONTENT)

    print("ADMIN_CREATIVE_ASSETS_STANDALONE_PAGE_INSTALLED")
    print(f"Backup: {BACKUP}")
    print(f"Created/updated: {PAGE_FILE}")
    print(f"Created/updated: {API_FILE}")
    print(f"Created/updated: {TEST_FILE}")

if __name__ == "__main__":
    main()