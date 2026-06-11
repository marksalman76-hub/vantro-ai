"use client";

import React, { useEffect, useMemo, useState } from "react";

type DirectMediaProviderPanelProps = {
  mode: "admin" | "client";
};

type ProviderStackItem = {
  provider: string;
  name?: string;
  category?: string;
  supports?: string[];
  configured?: boolean;
  direct_execution_enabled?: boolean;
  disabled_reason?: string;
  credential_values_exposed?: boolean;
  customer_safe?: boolean;
};

type DirectMediaStatus = {
  success?: boolean;
  direct_media_provider_execution_ready?: boolean;
  provider_stack?: ProviderStackItem[];
  provider_count?: number;
  configured_provider_count?: number;
  direct_execution_provider_count?: number;
  supported_video_providers?: string[];
  supported_audio_providers?: string[];
  runway?: ProviderStackItem;
  kling?: ProviderStackItem;
  heygen?: ProviderStackItem;
  elevenlabs?: ProviderStackItem;
  replicate?: ProviderStackItem;
  openai?: ProviderStackItem;
  sync?: ProviderStackItem;
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

const FALLBACK_PROVIDER_STACK: ProviderStackItem[] = [
  { provider: "runway", name: "Runway", supports: ["video"], configured: false, direct_execution_enabled: true },
  { provider: "kling", name: "Kling", supports: ["video"], configured: false, direct_execution_enabled: true },
  { provider: "heygen", name: "HeyGen", supports: ["video", "avatar_video"], configured: false, direct_execution_enabled: false, disabled_reason: "Direct adapter pending" },
  { provider: "elevenlabs", name: "ElevenLabs", supports: ["audio", "voiceover"], configured: false, direct_execution_enabled: true },
  { provider: "replicate", name: "Replicate", supports: ["image", "video"], configured: false, direct_execution_enabled: false, disabled_reason: "Direct adapter pending" },
  { provider: "openai", name: "OpenAI", supports: ["image", "text"], configured: false, direct_execution_enabled: false, disabled_reason: "Direct media adapter pending" },
  { provider: "sync", name: "Sync / lip-sync", supports: ["lip_sync", "video"], configured: false, direct_execution_enabled: false, disabled_reason: "Direct adapter pending" },
];

function mediaTypeSupported(provider: ProviderStackItem | undefined, mediaType: string) {
  return Boolean(provider?.supports || []).valueOf() && Boolean(provider?.supports?.includes(mediaType));
}

function safeText(value: unknown, fallback = "") {
  return typeof value === "string" && value.trim() ? value.trim() : fallback;
}

function displayProviderStatus(provider: ProviderStackItem) {
  if (!provider.configured) return "not configured";
  if (!provider.direct_execution_enabled) return provider.disabled_reason || "display only";
  return "ready";
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
  const [pollingJobId, setPollingJobId] = useState("");
  const [compact, setCompact] = useState(false);
  const [latestVideoJobId, setLatestVideoJobId] = useState("");
  const [latestAudioJobId, setLatestAudioJobId] = useState("");
  const [composing, setComposing] = useState(false);
  const [compositionMessage, setCompositionMessage] = useState("");
  const [compositionResult, setCompositionResult] = useState<DirectMediaResult | null>(null);

  const providerStack = useMemo(() => {
    const remoteStack = Array.isArray(status?.provider_stack) ? status?.provider_stack || [] : [];
    return remoteStack.length ? remoteStack : FALLBACK_PROVIDER_STACK;
  }, [status]);

  const selectedProvider = useMemo(
    () => providerStack.find((item) => item.provider === provider) || providerStack[0],
    [provider, providerStack]
  );

  const canRun =
    isAdmin &&
    Boolean(selectedProvider?.configured) &&
    Boolean(selectedProvider?.direct_execution_enabled) &&
    mediaTypeSupported(selectedProvider, mediaType) &&
    Boolean(prompt.trim()) &&
    !running;

  const proxiedAssetUrl = result?.job_id ? `/api/admin-direct-media-provider-asset?job_id=${encodeURIComponent(result.job_id)}` : "";
  const previewUrl = safeText(
    result?.preview_url ||
      result?.provider_result?.video_url_preview ||
      (result?.playable && result?.download_ready ? proxiedAssetUrl : "")
  );
  const resultStatus = safeText(result?.status || result?.provider_status || result?.provider_result?.status, "Not run yet");

  async function loadStatus() {
    setStatusLoading(true);
    try {
      const response = await fetch("/api/admin-direct-media-provider-status", { cache: "no-store" });
      const data = await response.json();
      setStatus(data);
      if (Array.isArray(data?.provider_stack) && !data.provider_stack.some((item: ProviderStackItem) => item.provider === provider)) {
        setProvider(data.provider_stack[0]?.provider || "runway");
      }
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

  async function pollDirectMediaJob(jobId: string) {
    try {
      const response = await fetch(`/api/admin-direct-media-provider-job-status?job_id=${encodeURIComponent(jobId)}`, {
        cache: "no-store",
      });
      const data = await response.json();
      setResult(data);

      if (data?.status === "completed" && data?.playable) {
        setMessage("Direct media generated successfully. Preview is ready.");
        if (data?.media_type === "video" && data?.job_id) setLatestVideoJobId(data.job_id);
        if (data?.media_type === "audio" && data?.job_id) setLatestAudioJobId(data.job_id);
        setCompact(false);
        setPollingJobId("");
        return;
      }

      if (String(data?.status || "").includes("failed") || String(data?.status || "").includes("exception") || String(data?.status || "").includes("blocked")) {
        setMessage(data?.message || data?.error || data?.status || "Direct media job stopped before producing a playable asset.");
        setPollingJobId("");
        return;
      }

      setMessage(`Direct media job ${data?.status || "running"}. Polling for completion...`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to poll direct media job.");
    }
  }

  async function runDirectMediaGeneration() {
    if (!isAdmin) {
      setMessage("Client workspaces can view safe generated media. Live provider spend remains owner/admin controlled.");
      return;
    }

    if (!canRun) {
      setMessage(
        !selectedProvider?.configured
          ? `${selectedProvider?.name || provider} is not configured yet. Add provider credentials before execution.`
          : !selectedProvider?.direct_execution_enabled
            ? `${selectedProvider?.name || provider} is visible in the stack, but its direct adapter is not enabled yet.`
            : "Select a matching provider, media type, and prompt first."
      );
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

      if (data?.job_id && (data?.polling_required || data?.status === "queued" || data?.status === "running")) {
        setPollingJobId(data.job_id);
        setMessage("Direct media job accepted. Polling for completion...");
        setCompact(true);
      } else if (data?.success && data?.playable) {
        setResult(data);
        if (data?.media_type === "video" && data?.job_id) setLatestVideoJobId(data.job_id);
        if (data?.media_type === "audio" && data?.job_id) setLatestAudioJobId(data.job_id);
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
    if (!pollingJobId) return;

    const timer = window.setInterval(() => {
      pollDirectMediaJob(pollingJobId);
    }, 5000);

    pollDirectMediaJob(pollingJobId);

    return () => window.clearInterval(timer);
  }, [pollingJobId]);

  useEffect(() => {
    loadStatus();
  }, []);

  useEffect(() => {
    const supports = selectedProvider?.supports || [];
    if (supports.length && !supports.includes(mediaType)) {
      setMediaType(supports.includes("video") ? "video" : supports.includes("audio") ? "audio" : supports[0]);
    }

    if (provider === "elevenlabs" && prompt.toLowerCase().includes("video")) {
      setPrompt("Create a short premium ecommerce product voiceover for a clean 5 second product promo.");
    }
  }, [provider, selectedProvider?.supports?.join("|")]);


  async function composeLatestVideoAndAudio() {
    if (!isAdmin) {
      setCompositionMessage("Composition is owner/admin controlled.");
      return;
    }

    const videoJobId = latestVideoJobId.trim();
    const audioJobId = latestAudioJobId.trim();

    if (!videoJobId || !audioJobId) {
      setCompositionMessage("Generate or enter one completed video job and one completed audio job first.");
      return;
    }

    setComposing(true);
    setCompositionMessage("Composing final MP4 with video and audio...");
    setCompositionResult(null);

    try {
      const response = await fetch("/api/admin-direct-media-provider-compose", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        cache: "no-store",
        body: JSON.stringify({
          video_job_id: videoJobId,
          audio_job_id: audioJobId,
        }),
      });

      const data = await response.json();
      setCompositionResult(data);

      if (data?.success && data?.playable) {
        setResult(data);
        setCompositionMessage("Final composed video with audio is ready.");
      } else {
        setCompositionMessage(data?.reason || data?.message || data?.error || data?.status || "Composition did not produce a playable MP4.");
      }
    } catch (error) {
      setCompositionResult({
        success: false,
        status: "composition_frontend_failed",
        message: error instanceof Error ? error.message : "Composition failed.",
        credential_values_exposed: false,
        customer_safe: true,
      });
      setCompositionMessage("Composition failed.");
    } finally {
      setComposing(false);
    }
  }

  const shellStyle: React.CSSProperties = {
    border: isAdmin ? "1px solid rgba(34,211,238,.24)" : "1px solid rgba(129,140,248,.20)",
    borderRadius: 22,
    padding: compact ? 12 : 18,
    margin: isAdmin ? "10px 0 18px" : "12px 0 22px",
    background: isAdmin
      ? "linear-gradient(135deg, rgba(8,47,73,.96), rgba(15,23,42,.96))"
      : "linear-gradient(135deg, rgba(255,255,255,.98), rgba(238,242,255,.96))",
    boxShadow: isAdmin ? "0 18px 42px rgba(8,47,73,.22)" : "0 14px 34px rgba(79,70,229,.10)",
    color: isAdmin ? "#e0f2fe" : "#0f172a",
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
          <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.55, color: isAdmin ? "#bae6fd" : "#475569", maxWidth: 800 }}>
            {isAdmin
              ? "Choose an agent, provider, media type and prompt. The full media stack is visible, while live execution remains limited to configured direct adapters."
              : "Generated media from the direct provider lane appears in the workspace once owner/admin execution is completed."}
          </p>
        </div>

        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <button type="button" onClick={() => setCompact((value) => !value)} style={{ border: "none", borderRadius: 999, padding: "9px 13px", background: isAdmin ? "rgba(99,102,241,.25)" : "rgba(79,70,229,.10)", color: isAdmin ? "#e0f2fe" : "#4338ca", fontWeight: 950, cursor: "pointer" }}>
            {compact ? "Expand panel" : "Compact panel"}
          </button>
          <button type="button" onClick={loadStatus} style={{ border: "none", borderRadius: 999, padding: "9px 13px", background: isAdmin ? "rgba(34,211,238,.20)" : "rgba(79,70,229,.10)", color: isAdmin ? "#e0f2fe" : "#4338ca", fontWeight: 950, cursor: "pointer" }}>
            {statusLoading ? "Checking..." : "Refresh status"}
          </button>
        </div>
      </div>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 14 }}>
        {providerStack.map((item) => (
          <span key={item.provider} style={pillStyle}>
            {item.name || item.provider}: {displayProviderStatus(item)}
          </span>
        ))}
        <span style={pillStyle}>Secrets exposed: {status?.credential_values_exposed ? "yes" : "no"}</span>
        {pollingJobId ? <span style={pillStyle}>Polling: {pollingJobId}</span> : null}
      </div>

      {!compact ? (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: 10, marginTop: 14 }}>
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
                {providerStack.map((item) => (
                  <option key={item.provider} value={item.provider}>
                    {item.name || item.provider} — {displayProviderStatus(item)}
                  </option>
                ))}
              </select>
            </label>

            <label style={labelStyle}>
              Media type
              <select value={mediaType} onChange={(event) => setMediaType(event.target.value)} disabled={!isAdmin} style={inputStyle}>
                <option value="video">Video</option>
                <option value="audio">Audio</option>
                <option value="image">Image</option>
                <option value="avatar_video">Avatar video</option>
                <option value="lip_sync">Lip-sync</option>
                <option value="text">Text</option>
              </select>
            </label>
          </div>

          <label style={{ ...labelStyle, marginTop: 12 }}>
            Prompt
            <textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} disabled={!isAdmin} rows={4} style={{ ...inputStyle, resize: "vertical", lineHeight: 1.55 }} />
          </label>

          <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap", marginTop: 14 }}>
            <button type="button" onClick={runDirectMediaGeneration} disabled={!canRun} style={{ border: "none", borderRadius: 999, padding: "11px 16px", background: canRun ? "linear-gradient(135deg,#06b6d4,#6366f1)" : "rgba(148,163,184,.35)", color: "#ffffff", fontWeight: 950, cursor: canRun ? "pointer" : "not-allowed", boxShadow: canRun ? "0 12px 26px rgba(14,165,233,.22)" : "none" }}>
              {running ? "Generating..." : isAdmin ? "Generate direct media" : "Owner/admin controlled"}
            </button>

            {message ? <span style={{ fontSize: 12.5, fontWeight: 850, color: isAdmin ? "#bae6fd" : "#475569" }}>{message}</span> : null}
          </div>


          {/* DIRECT_MEDIA_COMPOSITION_PANEL_CONTROLS_V1 */}
          {isAdmin ? (
            <div
              style={{
                marginTop: 14,
                borderRadius: 18,
                padding: 14,
                background: "rgba(2,6,23,.36)",
                border: "1px solid rgba(125,211,252,.18)",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", gap: 10, flexWrap: "wrap", alignItems: "center" }}>
                <div>
                  <div style={{ fontSize: 12, fontWeight: 950, color: isAdmin ? "#f8fafc" : "#0f172a" }}>
                    Compose final video with audio
                  </div>
                  <p style={{ margin: "4px 0 0", fontSize: 12.5, color: isAdmin ? "#bae6fd" : "#64748b" }}>
                    Use one completed Runway video job and one completed ElevenLabs audio job to create a final MP4.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={composeLatestVideoAndAudio}
                  disabled={composing || !latestVideoJobId.trim() || !latestAudioJobId.trim()}
                  style={{
                    border: "none",
                    borderRadius: 999,
                    padding: "10px 14px",
                    background: composing || !latestVideoJobId.trim() || !latestAudioJobId.trim()
                      ? "rgba(148,163,184,.35)"
                      : "linear-gradient(135deg,#22c55e,#06b6d4)",
                    color: "#ffffff",
                    fontWeight: 950,
                    cursor: composing || !latestVideoJobId.trim() || !latestAudioJobId.trim() ? "not-allowed" : "pointer",
                  }}
                >
                  {composing ? "Composing..." : "Compose video + audio"}
                </button>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 10, marginTop: 12 }}>
                <label style={labelStyle}>
                  Completed video job ID
                  <input
                    value={latestVideoJobId}
                    onChange={(event) => setLatestVideoJobId(event.target.value)}
                    placeholder="direct_media_job_..."
                    style={inputStyle}
                  />
                </label>
                <label style={labelStyle}>
                  Completed audio job ID
                  <input
                    value={latestAudioJobId}
                    onChange={(event) => setLatestAudioJobId(event.target.value)}
                    placeholder="direct_media_job_..."
                    style={inputStyle}
                  />
                </label>
              </div>

              {compositionMessage ? (
                <p style={{ margin: "10px 0 0", fontSize: 12.5, fontWeight: 850, color: isAdmin ? "#bae6fd" : "#475569" }}>
                  {compositionMessage}
                </p>
              ) : null}

              {compositionResult?.job_id ? (
                <div style={{ marginTop: 8, fontSize: 12, color: isAdmin ? "#bae6fd" : "#64748b" }}>
                  Composition job: <strong>{compositionResult.job_id}</strong> · Status: <strong>{compositionResult.status || "unknown"}</strong>
                </div>
              ) : null}
            </div>
          ) : null}


        </>
      ) : (
        <div style={{ marginTop: 12, fontSize: 12.5, fontWeight: 850, color: isAdmin ? "#bae6fd" : "#475569" }}>
          Panel compacted. Current status: <strong>{resultStatus}</strong>{pollingJobId ? ` · Polling ${pollingJobId}` : ""}. Use Expand panel to edit prompt or view preview.
        </div>
      )}

      <div style={{ marginTop: 14, borderRadius: 18, padding: 14, background: isAdmin ? "rgba(2,6,23,.42)" : "rgba(255,255,255,.82)", border: isAdmin ? "1px solid rgba(125,211,252,.18)" : "1px solid rgba(148,163,184,.22)" }}>
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
              <video controls src={previewUrl} style={{ width: "100%", maxHeight: 220, borderRadius: 14, background: "#000" }} />
            )}
            <div style={{ marginTop: 10, display: "flex", gap: 10, flexWrap: "wrap" }}>
              <a href={previewUrl} target="_blank" rel="noreferrer" style={{ ...pillStyle, textDecoration: "none" }}>Open preview</a>
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
