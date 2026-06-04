"use client";

import { useEffect, useMemo, useState } from "react";

type CreativeMediaAsset = {
  asset_id?: string | null;
  provider?: string | null;
  provider_key?: string | null;
  asset_type?: string | null;
  media_type?: string | null;
  title?: string | null;
  file_name?: string | null;
  local_path?: string | null;
  metadata_path?: string | null;
  provider_asset_url?: string | null;
  preview_url?: string | null;
  download_url?: string | null;
  content?: string | null;
  summary?: string | null;
  size_bytes?: number | null;
  test_label?: string | null;
  task_id?: string | null;
  provider_asset_id?: string | null;
  status?: string | null;
  preview_ready?: boolean | null;
  download_ready?: boolean | null;
  customer_safe?: boolean | null;
  created_at?: string | null;
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

function getPreviewUrl(asset: CreativeMediaAsset): string {
  return (
    asset.preview_url ||
    asset.provider_asset_url ||
    asset.download_url ||
    ""
  ).trim();
}

function getDownloadUrl(asset: CreativeMediaAsset): string {
  return (
    asset.download_url ||
    asset.provider_asset_url ||
    asset.preview_url ||
    ""
  ).trim();
}

function isBrowserSafeUrl(url: string): boolean {
  return url.startsWith("http://") || url.startsWith("https://") || url.startsWith("data:");
}

function isLocalRenderPath(url: string): boolean {
  return url.startsWith("/opt/render/") || url.includes("/runtime_outputs/");
}

function getAssetLabel(asset: CreativeMediaAsset): string {
  return (
    asset.title ||
    asset.test_label ||
    asset.file_name ||
    asset.asset_id ||
    "Creative media asset"
  );
}

function getAssetType(asset: CreativeMediaAsset): string {
  return (asset.asset_type || asset.media_type || "asset").toLowerCase();
}

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
            No generated media assets found yet. Run a governed creative media execution, then refresh this page.
          </section>
        ) : (
          <section style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit,minmax(360px,1fr))",
            gap: "18px"
          }}>
            {assets.map((asset, index) => (
              <AssetCard key={`${asset.asset_id || asset.provider_asset_id || index}`} asset={asset} />
            ))}
          </section>
        )}
      </div>
    </main>
  );
}

function AssetCard({ asset }: { asset: CreativeMediaAsset }) {
  const previewUrl = useMemo(() => getPreviewUrl(asset), [asset]);
  const downloadUrl = useMemo(() => getDownloadUrl(asset), [asset]);
  const assetType = getAssetType(asset);
  const hasPreview = Boolean(previewUrl);
  const hasDownload = Boolean(downloadUrl);
  const browserPreview = hasPreview && isBrowserSafeUrl(previewUrl);
  const browserDownload = hasDownload && isBrowserSafeUrl(downloadUrl);
  const localDownloadPath = hasDownload && isLocalRenderPath(downloadUrl);

  return (
    <article style={{
      border: "1px solid rgba(148,163,184,.22)",
      background: "rgba(15,23,42,.82)",
      borderRadius: "18px",
      padding: "18px",
      boxShadow: "0 18px 48px rgba(0,0,0,.28)"
    }}>
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
          {asset.provider || asset.provider_key || "provider"}
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
          {assetType}
        </span>
      </div>

      <h2 style={{fontSize: "16px", color: "white", wordBreak: "break-word"}}>
        {getAssetLabel(asset)}
      </h2>

      <div style={{marginTop: "14px", display: "grid", gap: "8px", color: "#cbd5e1", fontSize: "13px"}}>
        <p>Status: <strong style={{color: "white"}}>{asset.status || "ready"}</strong></p>
        <p>Preview ready: <strong style={{color: "white"}}>{hasPreview ? "Yes" : "No"}</strong></p>
        <p>Download ready: <strong style={{color: "white"}}>{hasDownload ? "Yes" : "No"}</strong></p>
        <p>Size: <strong style={{color: "white"}}>{asset.size_bytes ? `${Math.round(asset.size_bytes / 1024)} KB` : "Unknown"}</strong></p>
      </div>

      {browserPreview ? (
        <div style={{marginTop: "16px"}}>
          {assetType.includes("video") ? (
            <video
              src={previewUrl}
              controls
              style={{width: "100%", borderRadius: "14px", border: "1px solid rgba(148,163,184,.2)"}}
            />
          ) : assetType.includes("audio") ? (
            <audio
              src={previewUrl}
              controls
              style={{width: "100%"}}
            />
          ) : assetType.includes("image") ? (
            <img
              src={previewUrl}
              alt={getAssetLabel(asset)}
              style={{width: "100%", borderRadius: "14px", border: "1px solid rgba(148,163,184,.2)"}}
            />
          ) : (
            <a href={previewUrl} target="_blank" rel="noreferrer" style={{color: "#67e8f9", fontWeight: 900}}>
              Open preview
            </a>
          )}
        </div>
      ) : null}

      <div style={{
        marginTop: "14px",
        display: "flex",
        flexWrap: "wrap",
        gap: "10px"
      }}>
        {browserPreview ? (
          <a
            href={previewUrl}
            target="_blank"
            rel="noreferrer"
            style={buttonLinkStyle}
          >
            Open preview
          </a>
        ) : null}

        {browserDownload ? (
          <a
            href={downloadUrl}
            target="_blank"
            rel="noreferrer"
            download
            style={buttonLinkStyle}
          >
            Download / open file
          </a>
        ) : null}
      </div>

      <div style={{
        marginTop: "14px",
        border: "1px solid rgba(148,163,184,.18)",
        background: "rgba(2,6,23,.65)",
        borderRadius: "12px",
        padding: "12px"
      }}>
        <p style={{fontSize: "11px", color: "#64748b", textTransform: "uppercase", fontWeight: 900, marginBottom: "8px"}}>
          Asset URL / path
        </p>
        <p style={{fontSize: "12px", color: "#e2e8f0", wordBreak: "break-all"}}>
          {previewUrl || downloadUrl || asset.local_path || "Not available"}
        </p>
        {localDownloadPath ? (
          <p style={{fontSize: "12px", color: "#fbbf24", marginTop: "8px"}}>
            Stored on Render runtime. Use the preview URL for browser playback.
          </p>
        ) : null}
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
  );
}

const buttonLinkStyle: React.CSSProperties = {
  color: "#a5f3fc",
  background: "rgba(8,145,178,.15)",
  border: "1px solid rgba(34,211,238,.4)",
  borderRadius: "12px",
  padding: "10px 12px",
  fontWeight: 900,
  textDecoration: "none",
  fontSize: "13px"
};

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