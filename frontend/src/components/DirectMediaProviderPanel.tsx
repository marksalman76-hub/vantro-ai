"use client";

import React, { useEffect, useMemo, useState } from "react";

type DirectMediaProviderPanelProps = {
  mode: "admin" | "client";
};

type DirectMediaStatus = {
  success?: boolean;
  direct_media_provider_execution_ready?: boolean;
  supported_video_providers?: string[];
  supported_audio_providers?: string[];
  runway?: { configured?: boolean };
  kling?: { configured?: boolean };
  elevenlabs?: { configured?: boolean };
  credential_values_exposed?: boolean;
  customer_safe?: boolean;
  error?: string;
  message?: string;
};

type DirectMediaResult = {
  success?: boolean;
  job_id?: string;
  status?: string;
  agent_id?: string;
  provider?: string;
  media_type?: string;
  provider_status?: string;
  provider_job_id?: string;
  playable?: boolean;
  preview_ready?: boolean;
  download_ready?: boolean;
  preview_url?: string;
  download_url?: string;
  video_size_bytes?: number;
  credential_values_exposed?: boolean;
  customer_safe?: boolean;
  error?: string;
  message?: string;
  provider_result?: {
    video_size_bytes?: number;
    video_url_preview?: string;
    status?: string;
    task_id?: string;
  };
};

const AGENT_OPTIONS = [
  ["social_media_manager_content_creator_agent", "Social Media Manager Agent"],
  ["ugc_creative_agent", "UGC Creative Agent"],
  ["paid_ads_agent", "Paid Ads Agent"],
  ["product_image_agent", "Product Image Agent"],
  ["marketing_specialist_agent", "Marketing Specialist Agent"],
];

const PROVIDER_OPTIONS = [
  ["runway", "Runway video"],
  ["elevenlabs", "ElevenLabs audio"],
  ["kling", "Kling video"],
];

function providerSupportsMedia(provider: string, mediaType: string) {
  if (provider === "elevenlabs") return mediaType === "audio";
  if (provider === "runway" || provider === "kling") return mediaType === "video";
  return false;
}

function safeText(value: unknown, fallback = "") {
  return typeof value === "string" && value.trim() ? value.trim() : fallback;
}

export default function DirectMediaProviderPanel({ mode }: DirectMediaProviderPanelProps) {
  const isAdmin = mode === "admin";
  const [status, setStatus] = useState<DirectMediaStatus | null>(null);
  const [statusLoading, setStatusLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [agentId, setAgentId] = useState("social_media_manager_content_creator_agent");
  const [provider, setProvider] = useState("runway");
  const [mediaType, setMediaType] = useState("video");
  const [prompt, setPrompt] = useState(
    "Create a simple 5 second ecommerce product promo video with clean product lighting and slow camera motion."
  );
  const [result, setResult] = useState<DirectMediaResult | null>(null);
  const [message, setMessage] = useState("");

  const providerReady = useMemo(() => {
    if (!status) return false;
    if (provider === "runway") return Boolean(status.runway?.configured);
    if (provider === "kling") return Boolean(status.kling?.configured);
    if (provider === "elevenlabs") return Boolean(status.elevenlabs?.configured);
    return false;
  }, [provider, status]);

  const canRun = isAdmin && providerReady && providerSupportsMedia(provider, mediaType) && Boolean(prompt.trim()) && !running;
  const previewUrl = safeText(result?.preview_url || result?.provider_result?.video_url_preview);
  const resultStatus = safeText(result?.status || result?.provider_status || result?.provider_result?.status, "Not run yet");

  async function loadStatus() {
    setStatusLoading(true);
    try {
      const response = await fetch("/api/admin-direct-media-provider-status", { cache: "no-store" });
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      setStatus({
        success: false,
        error: "status_load_failed",
        message: error instanceof Error ? error.message : "Unable to load direct media provider status.",
        credential_values_exposed: false,
        customer_safe: true,
      });
    } finally {
      setStatusLoading(false);
    }
  }

  async function runDirectMediaGeneration() {
    if (!isAdmin) {
      setMessage("Client workspaces can view safe generated media. Live provider spend remains owner/admin controlled.");
      return;
    }

    if (!canRun) {
      setMessage("Select a configured provider, matching media type, and prompt first.");
      return;
    }

    setRunning(true);
    setMessage("Direct provider generation started. This can take one to two minutes for video.");
    setResult(null);

    try {
      const response = await fetch("/api/admin-direct-media-provider-execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        cache: "no-store",
        body: JSON.stringify({
          agent_id: agentId,
          provider,
          media_type: mediaType,
          prompt,
        }),
      });

      const data = await response.json();
      setResult(data);

      if (data?.success && data?.playable) {
        setMessage("Direct media generated successfully. Preview is ready.");
      } else {
        setMessage(data?.message || data?.error || data?.status || "Direct media provider execution completed with no playable asset.");
      }
    } catch (error) {
      setResult({
        success: false,
        status: "frontend_execute_failed",
        message: error instanceof Error ? error.message : "Direct media generation failed.",
        credential_values_exposed: false,
        customer_safe: true,
      });
      setMessage("Direct media generation failed.");
    } finally {
      setRunning(false);
    }
  }

  useEffect(() => {
    loadStatus();
  }, []);

  useEffect(() => {
    if (provider === "elevenlabs") {
      setMediaType("audio");
      if (prompt.toLowerCase().includes("video")) {
        setPrompt("Create a short premium ecommerce product voiceover for a clean 5 second product promo.");
      }
    } else if (mediaType === "audio") {
      setMediaType("video");
    }
  }, [provider]);

  const shellStyle: React.CSSProperties = {
    border: isAdmin ? "1px solid rgba(34,211,238,.24)" : "1px solid rgba(129,140,248,.20)",
    borderRadius: 22,
    padding: 18,
    margin: isAdmin ? "18px 0" : "18px 0 22px",
    background: isAdmin
      ? "linear-gradient(135deg, rgba(8,47,73,.96), rgba(15,23,42,.96))"
      : "linear-gradient(135deg, rgba(255,255,255,.98), rgba(238,242,255,.96))",
    boxShadow: isAdmin ? "0 18px 42px rgba(8,47,73,.22)" : "0 14px 34px rgba(79,70,229,.10)",
    color: isAdmin ? "#e0f2fe" : "#0f172a",
  };

  const gridStyle: React.CSSProperties = {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))",
    gap: 10,
    marginTop: 14,
  };

  const inputStyle: React.CSSProperties = {
    width: "100%",
    borderRadius: 14,
    border: isAdmin ? "1px solid rgba(125,211,252,.28)" : "1px solid rgba(148,163,184,.35)",
    padding: "10px 12px",
    background: isAdmin ? "rgba(15,23,42,.72)" : "#ffffff",
    color: isAdmin ? "#f8fafc" : "#0f172a",
    fontWeight: 750,
    fontSize: 13,
    outline: "none",
  };

  const labelStyle: React.CSSProperties = {
    display: "grid",
    gap: 6,
    fontSize: 11,
    fontWeight: 950,
    letterSpacing: ".11em",
    textTransform: "uppercase",
    color: isAdmin ? "#bae6fd" : "#64748b",
  };

  const pillStyle: React.CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    gap: 6,
    borderRadius: 999,
    padding: "7px 10px",
    fontSize: 11,
    fontWeight: 950,
    background: isAdmin ? "rgba(14,165,233,.18)" : "rgba(79,70,229,.08)",
    color: isAdmin ? "#bae6fd" : "#4338ca",
    border: isAdmin ? "1px solid rgba(125,211,252,.24)" : "1px solid rgba(79,70,229,.13)",
  };

  return (
    <section style={shellStyle}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "flex-start", flexWrap: "wrap" }}>
        <div>
          <div style={{ fontSize: 11, fontWeight: 950, letterSpacing: ".18em", textTransform: "uppercase", color: isAdmin ? "#67e8f9" : "#4f46e5" }}>
            Direct media provider lane
          </div>
          <h3 style={{ margin: "6px 0 4px", fontSize: 21, color: isAdmin ? "#f8fafc" : "#111827" }}>
            {isAdmin ? "Generate media with selected software" : "Direct media generation status"}
          </h3>
          <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.55, color: isAdmin ? "#bae6fd" : "#475569", maxWidth: 760 }}>
            {isAdmin
              ? "Choose an agent, provider, media type and prompt. This uses the verified direct provider execution path instead of the old queued media workflow."
              : "Generated media from the direct provider lane appears in the workspace once owner/admin execution is completed. Live paid provider execution remains owner/admin controlled."}
          </p>
        </div>
        <button
          type="button"
          onClick={loadStatus}
          style={{
            border: "none",
            borderRadius: 999,
            padding: "9px 13px",
            background: isAdmin ? "rgba(34,211,238,.20)" : "rgba(79,70,229,.10)",
            color: isAdmin ? "#e0f2fe" : "#4338ca",
            fontWeight: 950,
            cursor: "pointer",
          }}
        >
          {statusLoading ? "Checking..." : "Refresh status"}
        </button>
      </div>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 14 }}>
        <span style={pillStyle}>Runway: {status?.runway?.configured ? "ready" : "not configured"}</span>
        <span style={pillStyle}>ElevenLabs: {status?.elevenlabs?.configured ? "ready" : "not configured"}</span>
        <span style={pillStyle}>Kling: {status?.kling?.configured ? "ready" : "not configured"}</span>
        <span style={pillStyle}>Secrets exposed: {status?.credential_values_exposed ? "yes" : "no"}</span>
      </div>

      <div style={gridStyle}>
        <label style={labelStyle}>
          Agent
          <select value={agentId} onChange={(event) => setAgentId(event.target.value)} disabled={!isAdmin} style={inputStyle}>
            {AGENT_OPTIONS.map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </label>

        <label style={labelStyle}>
          Provider
          <select value={provider} onChange={(event) => setProvider(event.target.value)} disabled={!isAdmin} style={inputStyle}>
            {PROVIDER_OPTIONS.map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </label>

        <label style={labelStyle}>
          Media type
          <select value={mediaType} onChange={(event) => setMediaType(event.target.value)} disabled={!isAdmin} style={inputStyle}>
            <option value="video">Video</option>
            <option value="audio">Audio</option>
          </select>
        </label>
      </div>

      <label style={{ ...labelStyle, marginTop: 12 }}>
        Prompt
        <textarea
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
          disabled={!isAdmin}
          rows={4}
          style={{ ...inputStyle, resize: "vertical", lineHeight: 1.55 }}
        />
      </label>

      <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap", marginTop: 14 }}>
        <button
          type="button"
          onClick={runDirectMediaGeneration}
          disabled={!canRun}
          style={{
            border: "none",
            borderRadius: 999,
            padding: "11px 16px",
            background: canRun ? "linear-gradient(135deg,#06b6d4,#6366f1)" : "rgba(148,163,184,.35)",
            color: "#ffffff",
            fontWeight: 950,
            cursor: canRun ? "pointer" : "not-allowed",
            boxShadow: canRun ? "0 12px 26px rgba(14,165,233,.22)" : "none",
          }}
        >
          {running ? "Generating..." : isAdmin ? "Generate direct media" : "Owner/admin controlled"}
        </button>

        {message ? (
          <span style={{ fontSize: 12.5, fontWeight: 850, color: isAdmin ? "#bae6fd" : "#475569" }}>{message}</span>
        ) : null}
      </div>

      <div
        style={{
          marginTop: 14,
          borderRadius: 18,
          padding: 14,
          background: isAdmin ? "rgba(2,6,23,.42)" : "rgba(255,255,255,.82)",
          border: isAdmin ? "1px solid rgba(125,211,252,.18)" : "1px solid rgba(148,163,184,.22)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", gap: 10, flexWrap: "wrap" }}>
          <div>
            <div style={{ fontSize: 12, fontWeight: 950, color: isAdmin ? "#f8fafc" : "#0f172a" }}>Latest direct media result</div>
            <div style={{ marginTop: 4, fontSize: 12, color: isAdmin ? "#bae6fd" : "#64748b" }}>
              Status: <strong>{resultStatus}</strong>
              {result?.job_id ? <> · Job: <strong>{result.job_id}</strong></> : null}
              {result?.provider_job_id ? <> · Provider job: <strong>{result.provider_job_id}</strong></> : null}
            </div>
          </div>
          <div style={{ fontSize: 12, fontWeight: 950, color: result?.credential_values_exposed ? "#ef4444" : "#22c55e" }}>
            Credentials exposed: {result?.credential_values_exposed ? "yes" : "no"}
          </div>
        </div>

        {previewUrl ? (
          <div style={{ marginTop: 12 }}>
            {result?.media_type === "audio" ? (
              <audio controls src={previewUrl} style={{ width: "100%" }} />
            ) : (
              <video controls src={previewUrl} style={{ width: "100%", maxHeight: 320, borderRadius: 14, background: "#000" }} />
            )}
            <div style={{ marginTop: 10, display: "flex", gap: 10, flexWrap: "wrap" }}>
              <a href={previewUrl} target="_blank" rel="noreferrer" style={{ ...pillStyle, textDecoration: "none" }}>
                Open preview
              </a>
              <span style={pillStyle}>Playable: {result?.playable ? "yes" : "pending"}</span>
              <span style={pillStyle}>Preview: {result?.preview_ready ? "ready" : "pending"}</span>
              <span style={pillStyle}>Download: {result?.download_ready ? "ready" : "pending"}</span>
            </div>
          </div>
        ) : (
          <p style={{ margin: "10px 0 0", fontSize: 12.5, color: isAdmin ? "#bae6fd" : "#64748b" }}>
            {isAdmin ? "Run direct media generation to preview a real provider asset here." : "No direct media preview is attached yet."}
          </p>
        )}
      </div>
    </section>
  );
}
