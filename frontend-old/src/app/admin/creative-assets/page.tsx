"use client";

import React, { useEffect, useState } from "react";

function cleanAssetReference(value: any): string {
  const text = String(value || "");
  if (!text) return "";
  if (text.startsWith("data:")) return "Embedded generated asset reference hidden for clean admin display.";
  if (text.length > 320) return text.slice(0, 320) + "...";
  return text;
}

function isHugeEmbeddedAsset(value: any): boolean {
  const text = String(value || "");
  return text.startsWith("data:") || text.length > 1200;
}

function cleanAssetContent(value: any): string {
  const text = String(value || "");
  if (!text) return "";
  if (text.startsWith("{") && text.includes('"content"')) {
    try {
      const parsed = JSON.parse(text);
      return String(parsed.content || parsed.summary || parsed.asset_content || text);
    } catch {
      return text;
    }
  }
  return text;
}


type CreativeMediaAsset = {
  asset_id?: string | null;
  provider?: string | null;
  provider_key?: string | null;
  asset_type?: string | null;
  media_type?: string | null;
  title?: string | null;
  file_name?: string | null;
  provider_asset_url?: string | null;
  preview_url?: string | null;
  download_url?: string | null;
  original_preview_url?: string | null;
  original_download_url?: string | null;
  size_bytes?: number | null;
  test_label?: string | null;
  provider_asset_id?: string | null;
  status?: string | null;
  created_at?: string | null;
  preview_ready?: boolean | null;
  download_ready?: boolean | null;
  playable?: boolean | null;
  metadata_only?: boolean | null;
  delivery_status?: string | null;
  not_playable_reason?: string | null;
};

type CreativeAssetsResponse = {
  success?: boolean;
  asset_count?: number;
  total_asset_count?: number;
  assets?: CreativeMediaAsset[];
  providers_checked?: string[];
  credential_values_exposed?: boolean;
  delivery_mode?: string;
  status?: string;
  error?: string;
};

function isSignedGatewayUrl(url?: string | null): boolean {
  const value = String(url || "").trim();
  return (
    value.includes("/asset-delivery/") &&
    value.includes("?") &&
    value.includes("expires=") &&
    value.includes("nonce=") &&
    value.includes("sig=")
  );
}

function isPlayableUrl(url?: string | null): boolean {
  const value = String(url || "").trim();
  if (!value || value.startsWith("data:")) return false;
  return isSignedGatewayUrl(value) || value.startsWith("http://") || value.startsWith("https://");
}


function isPlaceholderAsset(asset: CreativeMediaAsset): boolean {
  const status = String(asset.status || "").toLowerCase();
  const deliveryStatus = String(asset.delivery_status || "").toLowerCase();
  return Boolean(asset.metadata_only) || ["processing", "provider_job_created", "provider_polling", "metadata_only", "failed"].includes(deliveryStatus) || status.includes("live_provider_ready_endpoint_missing") || status.includes("endpoint_missing");
}

function getPreviewUrl(asset: CreativeMediaAsset): string {
  const value = String(asset.preview_url || "").trim();
  return asset.preview_ready && isPlayableUrl(value) ? value : "";
}

function getDownloadUrl(asset: CreativeMediaAsset): string {
  const value = String(asset.download_url || "").trim();
  return asset.download_ready && isPlayableUrl(value) ? value : "";
}

function getAssetType(asset: CreativeMediaAsset): string {
  return String(asset.asset_type || asset.media_type || "asset").toLowerCase();
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

function getNotPlayableMessage(asset: CreativeMediaAsset): string {
  const deliveryStatus = String(asset.delivery_status || "").replaceAll("_", " ");
  const reason = String(asset.not_playable_reason || "").replaceAll("_", " ");
  if (deliveryStatus || reason) {
    return `${deliveryStatus || "Not playable yet"}${reason ? `: ${reason}` : ""}`;
  }
  return "Processing or metadata-only asset. Playable media is not available yet.";
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
    <main style={pageStyle}>
      <div style={{ maxWidth: "1280px", margin: "0 auto" }}>
        <div style={headerStyle}>
          <div>
            <p style={eyebrowStyle}>Owner Command Centre</p>
            <h1 style={titleStyle}>Creative Media Assets</h1>
            <p style={subtitleStyle}>
              Generated audio and video outputs from ElevenLabs, Runway, Kling, HeyGen and Sync.
            </p>
          </div>

          <div style={{ display: "flex", gap: "10px" }}>
            <a href="/admin" style={secondaryButtonStyle}>Back to Admin</a>
            <button onClick={loadAssets} style={primaryButtonStyle}>
              {loading ? "Refreshing..." : "Refresh assets"}
            </button>
          </div>
        </div>

        <section style={metricsGridStyle}>
          <Metric label="Asset count" value={String(meta?.asset_count ?? assets.length)} />
          <Metric label="Total detected" value={String(meta?.total_asset_count ?? assets.length)} />
          <Metric label="Credential safe" value={meta?.credential_values_exposed === false ? "Yes" : "Check"} />
          <Metric label="Providers" value={(meta?.providers_checked || []).length ? String((meta?.providers_checked || []).length) : "6"} />
        </section>

        {error ? <section style={errorStyle}>{error}</section> : null}

        {loading ? (
          <section style={emptyStyle}>Loading generated media assets...</section>
        ) : assets.length === 0 ? (
          <section style={emptyStyle}>
            No generated media assets found yet. Run a governed creative media execution, then refresh this page.
          </section>
        ) : (
          <section style={assetGridStyle}>
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
  const assetType = getAssetType(asset);
  const previewUrl = getPreviewUrl(asset);
  const downloadUrl = getDownloadUrl(asset);
  const isPlaceholder = isPlaceholderAsset(asset);
  const hasPreview = Boolean(asset.preview_ready && previewUrl) && !isPlaceholder;
  const hasDownload = Boolean(asset.download_ready && downloadUrl) && !isPlaceholder;

  return (
    <article style={cardStyle}>
      <div style={cardTopStyle}>
        <span style={providerPillStyle}>{asset.provider || asset.provider_key || "provider"}</span>
        <span style={typePillStyle}>{assetType}</span>
      </div>

      <h2 style={assetTitleStyle}>{getAssetLabel(asset)}</h2>

      <div style={detailGridStyle}>
        <p>Status: <strong style={{ color: "white" }}>{asset.status || "ready"}</strong></p>
        <p>Preview ready: <strong style={{ color: "white" }}>{hasPreview ? "Yes" : "No"}</strong></p>
        <p>Download ready: <strong style={{ color: "white" }}>{hasDownload ? "Yes" : "No"}</strong></p>
        <p>Size: <strong style={{ color: "white" }}>{asset.size_bytes ? `${Math.round(asset.size_bytes / 1024)} KB` : "Unknown"}</strong></p>
      </div>

      {hasPreview ? (
        <div style={{ marginTop: "16px" }}>
          {assetType.includes("video") ? (
            <video
              key={previewUrl}
              src={previewUrl}
              controls
              preload="metadata"
              playsInline
              style={videoStyle}
            />
          ) : assetType.includes("audio") ? (
            <audio
              key={previewUrl}
              src={previewUrl}
              controls
              preload="metadata"
              style={{ width: "100%" }}
            />
          ) : assetType.includes("image") ? (
            <img
              src={previewUrl}
              alt={getAssetLabel(asset)}
              style={imageStyle}
            />
          ) : (
            <a href={previewUrl} target="_blank" rel="noreferrer" style={linkStyle}>
              Open preview
            </a>
          )}
        </div>
      ) : (
        <div style={warningBoxStyle}>
          {isPlaceholder
            ? getNotPlayableMessage(asset)
            : "Signed backend preview URL unavailable. This asset will not use the raw provider URL."}
        </div>
      )}

      <div style={buttonRowStyle}>
        {hasPreview ? (
          <a href={previewUrl} target="_blank" rel="noreferrer" style={linkButtonStyle}>
            Open preview
          </a>
        ) : null}

        {hasDownload ? (
          <a href={downloadUrl} target="_blank" rel="noreferrer" download style={linkButtonStyle}>
            Download / open file
          </a>
        ) : null}
      </div>

      <div style={urlBoxStyle}>
        <p style={urlLabelStyle}>Signed gateway URL</p>
        <p style={urlTextStyle}>{previewUrl || downloadUrl || "Not available"}</p>
      </div>

      {asset.original_preview_url || asset.provider_asset_url ? (
        <div style={urlBoxStyle}>
          <p style={urlLabelStyle}>Original provider URL / reference</p>
          <p style={urlTextStyle}>
            {isHugeEmbeddedAsset(asset.original_preview_url || asset.provider_asset_url)
              ? "Embedded generated provider reference hidden for clean admin display."
              : cleanAssetReference(asset.original_preview_url || asset.provider_asset_url)}
          </p>
          <p style={warningTextStyle}>Not used for browser playback.</p>
        </div>
      ) : null}
    </article>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div style={metricStyle}>
      <p style={metricLabelStyle}>{label}</p>
      <p style={metricValueStyle}>{value}</p>
    </div>
  );
}

const pageStyle: React.CSSProperties = {
  minHeight: "100vh",
  background: "#050816",
  color: "#e5e7eb",
  padding: "32px",
  fontFamily: "Inter, Arial, sans-serif",
};

const headerStyle: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  gap: "16px",
  alignItems: "center",
  marginBottom: "28px",
};

const eyebrowStyle: React.CSSProperties = {
  color: "#22d3ee",
  fontWeight: 900,
  fontSize: "12px",
  letterSpacing: ".2em",
  textTransform: "uppercase",
};

const titleStyle: React.CSSProperties = {
  fontSize: "34px",
  lineHeight: 1.1,
  marginTop: "8px",
  color: "white",
};

const subtitleStyle: React.CSSProperties = {
  color: "#94a3b8",
  marginTop: "8px",
};

const primaryButtonStyle: React.CSSProperties = {
  color: "#a5f3fc",
  background: "rgba(8,145,178,.15)",
  border: "1px solid rgba(34,211,238,.4)",
  borderRadius: "12px",
  padding: "10px 14px",
  fontWeight: 900,
  cursor: "pointer",
};

const secondaryButtonStyle: React.CSSProperties = {
  color: "#c4b5fd",
  border: "1px solid rgba(196,181,253,.35)",
  borderRadius: "12px",
  padding: "10px 14px",
  textDecoration: "none",
  fontWeight: 800,
};

const metricsGridStyle: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))",
  gap: "14px",
  marginBottom: "24px",
};

const assetGridStyle: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit,minmax(360px,1fr))",
  gap: "18px",
};

const cardStyle: React.CSSProperties = {
  border: "1px solid rgba(148,163,184,.22)",
  background: "rgba(15,23,42,.82)",
  borderRadius: "18px",
  padding: "18px",
  boxShadow: "0 18px 48px rgba(0,0,0,.28)",
};

const cardTopStyle: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  gap: "10px",
  marginBottom: "12px",
};

const providerPillStyle: React.CSSProperties = {
  color: "#67e8f9",
  background: "rgba(8,145,178,.12)",
  border: "1px solid rgba(34,211,238,.32)",
  borderRadius: "999px",
  padding: "6px 10px",
  fontSize: "12px",
  fontWeight: 900,
  textTransform: "uppercase",
};

const typePillStyle: React.CSSProperties = {
  color: "#c4b5fd",
  background: "rgba(124,58,237,.12)",
  border: "1px solid rgba(196,181,253,.25)",
  borderRadius: "999px",
  padding: "6px 10px",
  fontSize: "12px",
  fontWeight: 900,
  textTransform: "uppercase",
};

const assetTitleStyle: React.CSSProperties = {
  fontSize: "16px",
  color: "white",
  wordBreak: "break-word",
};

const detailGridStyle: React.CSSProperties = {
  marginTop: "14px",
  display: "grid",
  gap: "8px",
  color: "#cbd5e1",
  fontSize: "13px",
};

const videoStyle: React.CSSProperties = {
  width: "100%",
  borderRadius: "14px",
  border: "1px solid rgba(148,163,184,.2)",
  background: "#020617",
};

const imageStyle: React.CSSProperties = {
  width: "100%",
  borderRadius: "14px",
  border: "1px solid rgba(148,163,184,.2)",
};

const buttonRowStyle: React.CSSProperties = {
  marginTop: "14px",
  display: "flex",
  flexWrap: "wrap",
  gap: "10px",
};

const linkButtonStyle: React.CSSProperties = {
  color: "#a5f3fc",
  background: "rgba(8,145,178,.15)",
  border: "1px solid rgba(34,211,238,.4)",
  borderRadius: "12px",
  padding: "10px 12px",
  fontWeight: 900,
  textDecoration: "none",
  fontSize: "13px",
};

const linkStyle: React.CSSProperties = {
  color: "#67e8f9",
  fontWeight: 900,
};

const urlBoxStyle: React.CSSProperties = {
  marginTop: "14px",
  border: "1px solid rgba(148,163,184,.18)",
  background: "rgba(2,6,23,.65)",
  borderRadius: "12px",
  padding: "12px",
};

const urlLabelStyle: React.CSSProperties = {
  fontSize: "11px",
  color: "#64748b",
  textTransform: "uppercase",
  fontWeight: 900,
  marginBottom: "8px",
};

const urlTextStyle: React.CSSProperties = {
  fontSize: "12px",
  color: "#e2e8f0",
  wordBreak: "break-all",
};

const warningBoxStyle: React.CSSProperties = {
  marginTop: "14px",
  border: "1px solid rgba(251,191,36,.25)",
  background: "rgba(120,53,15,.18)",
  borderRadius: "12px",
  padding: "12px",
  color: "#fbbf24",
  fontSize: "13px",
};

const warningTextStyle: React.CSSProperties = {
  fontSize: "12px",
  color: "#fbbf24",
  marginTop: "8px",
};

const emptyStyle: React.CSSProperties = {
  border: "1px solid rgba(148,163,184,.2)",
  background: "rgba(15,23,42,.7)",
  borderRadius: "18px",
  padding: "22px",
  color: "#cbd5e1",
};

const errorStyle: React.CSSProperties = {
  border: "1px solid rgba(248,113,113,.35)",
  background: "rgba(127,29,29,.25)",
  borderRadius: "16px",
  padding: "16px",
  color: "#fecaca",
  marginBottom: "20px",
};

const metricStyle: React.CSSProperties = {
  border: "1px solid rgba(148,163,184,.2)",
  background: "rgba(15,23,42,.72)",
  borderRadius: "16px",
  padding: "16px",
};

const metricLabelStyle: React.CSSProperties = {
  fontSize: "11px",
  color: "#64748b",
  textTransform: "uppercase",
  fontWeight: 900,
  letterSpacing: ".12em",
};

const metricValueStyle: React.CSSProperties = {
  fontSize: "26px",
  color: "white",
  fontWeight: 950,
  marginTop: "6px",
};
