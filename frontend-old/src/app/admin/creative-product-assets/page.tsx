"use client";

import React, { DragEvent, useEffect, useRef, useState } from "react";

type UploadedAsset = {
  asset_id?: string;
  asset_type?: string;
  filename?: string;
  mime_type?: string;
  size_bytes?: number;
  created_at?: string;
  preview_ready?: boolean;
  download_ready?: boolean;
};

type AssetResponse = {
  success?: boolean;
  asset_count?: number;
  total_asset_count?: number;
  assets?: UploadedAsset[];
  allowed_extensions?: string[];
  error?: string;
};

const ASSET_TYPES = [
  ["product_image", "Product image"],
  ["product_video", "Product video"],
  ["logo", "Logo"],
  ["brand_guideline", "Brand guideline"],
  ["reference_asset", "Reference asset"],
  ["reference_video", "Reference video"],
  ["competitor_reference", "Competitor reference"],
  ["creative_brief", "Creative brief"],
];

const MAX_FILE_MB = 50;

function bytesToLabel(value?: number): string {
  if (!value) return "Unknown";
  if (value < 1024 * 1024) return `${Math.round(value / 1024)} KB`;
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

async function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = String(reader.result || "");
      const base64 = result.includes(",") ? result.split(",").pop() || "" : result;
      resolve(base64);
    };
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });
}

export default function CreativeProductAssetsPage() {
  const isAdmin = typeof window !== "undefined" && window.location.pathname.includes("/admin/");
  const listEndpoint = isAdmin ? "/api/admin-creative-product-assets" : "/api/client-creative-product-assets";
  const uploadEndpoint = isAdmin ? "/api/admin-creative-product-assets-upload" : "/api/client-creative-product-assets-upload";

  const [assetType, setAssetType] = useState("product_image");
  const [assets, setAssets] = useState<UploadedAsset[]>([]);
  const [meta, setMeta] = useState<AssetResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [message, setMessage] = useState("");
  const inputRef = useRef<HTMLInputElement | null>(null);

  async function loadAssets() {
    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(listEndpoint, { cache: "no-store" });
      const data: AssetResponse = await response.json();

      if (!response.ok || data.success === false) {
        throw new Error(data.error || "Unable to load assets");
      }

      setAssets(Array.isArray(data.assets) ? data.assets : []);
      setMeta(data);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : String(error));
    } finally {
      setLoading(false);
    }
  }

  async function uploadFiles(files: FileList | File[]) {
    const fileArray = Array.from(files || []);
    if (!fileArray.length) return;

    setUploading(true);
    setMessage(`Uploading ${fileArray.length} file(s)...`);

    try {
      for (const file of fileArray) {
        if (file.size > MAX_FILE_MB * 1024 * 1024) {
          throw new Error(`${file.name} is larger than ${MAX_FILE_MB}MB`);
        }

        const contentBase64 = await fileToBase64(file);

        const response = await fetch(uploadEndpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          cache: "no-store",
          body: JSON.stringify({
            tenant_id: "owner_admin",
            filename: file.name,
            content_base64: contentBase64,
            asset_type: assetType,
            uploaded_by: isAdmin ? "owner_admin" : "client",
            metadata: {
              browser_mime_type: file.type,
              source: isAdmin ? "admin_drag_drop_upload" : "client_drag_drop_upload",
            },
          }),
        });

        const data = await response.json();

        if (!response.ok || data.success === false) {
          throw new Error(data.status || data.error || `Upload failed for ${file.name}`);
        }
      }

      setMessage("Upload complete.");
      await loadAssets();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : String(error));
    } finally {
      setUploading(false);
      setDragging(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  function onDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setDragging(false);
    uploadFiles(event.dataTransfer.files);
  }

  useEffect(() => {
    loadAssets();
  }, []);

  return (
    <main style={pageStyle}>
      <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
        <div style={headerStyle}>
          <div>
            <p style={eyebrowStyle}>{isAdmin ? "Owner Command Centre" : "Client Workspace"}</p>
            <h1 style={titleStyle}>Creative Product Assets</h1>
            <p style={subtitleStyle}>
              Upload product images, logos, references, videos and brand files for the creative agent team.
            </p>
          </div>

          <a href={isAdmin ? "/admin/creative-assets" : "/client"} style={secondaryButtonStyle}>
            {isAdmin ? "Back to Creative Assets" : "Back to Workspace"}
          </a>
        </div>

        <section style={metricsGridStyle}>
          <Metric label="Asset count" value={String(meta?.asset_count ?? assets.length)} />
          <Metric label="Total uploaded" value={String(meta?.total_asset_count ?? assets.length)} />
          <Metric label="Upload status" value={uploading ? "Uploading" : "Ready"} />
          <Metric label="Max file" value={`${MAX_FILE_MB}MB`} />
        </section>

        <section
          onDragOver={(event) => {
            event.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          style={{
            ...dropZoneStyle,
            borderColor: dragging ? "rgba(34,211,238,.9)" : "rgba(148,163,184,.28)",
            background: dragging ? "rgba(8,145,178,.16)" : "rgba(15,23,42,.78)",
          }}
        >
          <p style={{ color: "#67e8f9", fontWeight: 950, fontSize: "18px" }}>
            Drag and drop product / brand files here
          </p>
          <p style={{ color: "#94a3b8", marginTop: "8px" }}>
            Supports JPG, PNG, WEBP, GIF, MP4, MOV, WEBM, PDF, DOCX, PPTX, TXT and Markdown.
          </p>

          <div style={{ marginTop: "16px", display: "flex", flexWrap: "wrap", gap: "10px", justifyContent: "center" }}>
            <select
              value={assetType}
              onChange={(event) => setAssetType(event.target.value)}
              style={selectStyle}
            >
              {ASSET_TYPES.map(([value, label]) => (
                <option value={value} key={value}>{label}</option>
              ))}
            </select>

            <button
              onClick={() => inputRef.current?.click()}
              disabled={uploading}
              style={primaryButtonStyle}
            >
              {uploading ? "Uploading..." : "Choose files"}
            </button>

            <button onClick={loadAssets} style={secondaryButtonStyle}>
              Refresh
            </button>
          </div>

          <input
            ref={inputRef}
            type="file"
            multiple
            hidden
            onChange={(event) => event.target.files ? uploadFiles(event.target.files) : undefined}
            accept=".jpg,.jpeg,.png,.webp,.gif,.mp4,.mov,.webm,.pdf,.docx,.pptx,.txt,.md"
          />
        </section>

        {message ? <section style={messageStyle}>{message}</section> : null}

        {loading ? (
          <section style={emptyStyle}>Loading uploaded creative product assets...</section>
        ) : assets.length === 0 ? (
          <section style={emptyStyle}>
            No product or brand assets uploaded yet.
          </section>
        ) : (
          <section style={assetGridStyle}>
            {assets.map((asset) => (
              <article key={asset.asset_id} style={cardStyle}>
                <div style={cardTopStyle}>
                  <span style={providerPillStyle}>{asset.asset_type || "asset"}</span>
                  <span style={typePillStyle}>{asset.mime_type || "file"}</span>
                </div>
                <h2 style={assetTitleStyle}>{asset.filename || asset.asset_id}</h2>
                <p style={detailTextStyle}>Size: <strong>{bytesToLabel(asset.size_bytes)}</strong></p>
                <p style={detailTextStyle}>Preview ready: <strong>{asset.preview_ready ? "Yes" : "No"}</strong></p>
                <p style={detailTextStyle}>Download ready: <strong>{asset.download_ready ? "Yes" : "No"}</strong></p>
                <p style={urlTextStyle}>{asset.asset_id}</p>
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

const metricsGridStyle: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))",
  gap: "14px",
  marginBottom: "24px",
};

const dropZoneStyle: React.CSSProperties = {
  border: "2px dashed rgba(148,163,184,.28)",
  borderRadius: "22px",
  padding: "38px",
  textAlign: "center",
  marginBottom: "20px",
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
  background: "rgba(15,23,42,.45)",
};

const selectStyle: React.CSSProperties = {
  color: "#e5e7eb",
  background: "#020617",
  border: "1px solid rgba(148,163,184,.35)",
  borderRadius: "12px",
  padding: "10px 12px",
  fontWeight: 800,
};

const messageStyle: React.CSSProperties = {
  border: "1px solid rgba(34,211,238,.25)",
  background: "rgba(8,145,178,.12)",
  color: "#a5f3fc",
  borderRadius: "14px",
  padding: "14px",
  marginBottom: "18px",
};

const emptyStyle: React.CSSProperties = {
  border: "1px solid rgba(148,163,184,.2)",
  background: "rgba(15,23,42,.7)",
  borderRadius: "18px",
  padding: "22px",
  color: "#cbd5e1",
};

const assetGridStyle: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit,minmax(300px,1fr))",
  gap: "18px",
};

const cardStyle: React.CSSProperties = {
  border: "1px solid rgba(148,163,184,.22)",
  background: "rgba(15,23,42,.82)",
  borderRadius: "18px",
  padding: "18px",
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
};

const assetTitleStyle: React.CSSProperties = {
  fontSize: "16px",
  color: "white",
  wordBreak: "break-word",
};

const detailTextStyle: React.CSSProperties = {
  color: "#cbd5e1",
  fontSize: "13px",
  marginTop: "8px",
};

const urlTextStyle: React.CSSProperties = {
  color: "#64748b",
  fontSize: "12px",
  wordBreak: "break-all",
  marginTop: "10px",
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
