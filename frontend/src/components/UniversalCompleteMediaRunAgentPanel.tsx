"use client";

import { useEffect, useMemo, useState } from "react";

type BusinessProfile = Record<string, any>;

type CompleteMediaConfig = {
  enabled: boolean;
  mode: "admin" | "client";
  prompt: string;
  output_type: string;
  platform: string;
  duration_seconds: string;
  aspect_ratio: string;
  language: string;
  accent: string;
  tone: string;
  voice_style: string;
  age_range: string;
  gender_presentation: string;
  ethnicity_or_cultural_appearance: string;
  avatar_likeness: string;
  facial_features: string;
  expressions: string;
  gestures: string;
  wardrobe: string;
  background_setting: string;
  visual_style: string;
  camera_movement: string;
  music_style: string;
  sound_effects: string;
  call_to_action: string;
  agent_id: string;
  selected_agent: string;
  selected_agents: string[];
  industry: string;
  target_audience: string;
  brand_style: string;
  product_or_service_details: string;
  speaking_pace: string;
  lip_sync_accuracy: string;
  final_delivery_format: string;
  run_direct_from_popup: boolean;
  native_popup_execution: boolean;
  creative_agent_direct_execution: boolean;
  requested_from: string;
  requested_at?: string;
};

const OUTPUT_TYPES = [
  "Complete video with voiceover",
  "UGC style video",
  "Avatar / presenter video",
  "Lip-sync video",
  "Explainer video",
  "Social media reel",
  "Advertisement",
  "Training clip",
  "Podcast intro",
  "Audio only",
  "Image with narration",
];

const PLATFORMS = [
  "General",
  "TikTok",
  "Instagram Reels",
  "YouTube Shorts",
  "YouTube",
  "Website",
  "Ad platform",
  "Training / course",
  "Presentation",
];

const DURATIONS = ["5", "10", "15", "30", "45", "60"];
const ASPECT_RATIOS = ["9:16", "1:1", "16:9", "4:5"];

const CREATIVE_AGENT_KEYWORDS = [
  "creative",
  "media",
  "video",
  "audio",
  "content",
  "social",
  "marketing",
  "brand",
  "ads",
  "advertising",
  "ugc",
  "copy",
  "website",
  "product",
  "ecommerce",
  "campaign",
  "image",
];

const DEFAULT_CREATIVE_AGENTS = [
  "ugc_creative_agent",
  "social_media_manager_content_creator_agent",
  "ad_creative_agent",
  "campaign_launch_agent",
  "creative_rotation_agent",
  "product_image_direction_agent",
  "product_copywriting_agent",
  "marketing_specialist_agent",
];

const POPUP_CREATIVE_AGENT_OPTIONS = [
  { value: "auto", label: "Auto-select best creative agent" },
  { value: "ugc_creative_agent", label: "UGC Creative Agent" },
  { value: "social_media_manager_content_creator_agent", label: "Social Media / Content Creator Agent" },
  { value: "ad_creative_agent", label: "Ad Creative Agent" },
  { value: "campaign_launch_agent", label: "Campaign Launch Agent" },
  { value: "creative_rotation_agent", label: "Creative Rotation Agent" },
  { value: "product_image_direction_agent", label: "Product Image Direction Agent" },
  { value: "product_copywriting_agent", label: "Product Copywriting Agent" },
  { value: "marketing_specialist_agent", label: "Marketing Specialist Agent" },
];


function isCreativeAgent(agent: string) {
  const value = String(agent || "").toLowerCase();
  return CREATIVE_AGENT_KEYWORDS.some((keyword) => value.includes(keyword));
}

function fieldStyle(mode: "admin" | "client") {
  return {
    borderRadius: 12,
    border: "1px solid rgba(148,163,184,.38)",
    padding: "9px 10px",
    fontSize: 12.5,
    background: mode === "admin" ? "rgba(15,23,42,.92)" : "#fff",
    color: mode === "admin" ? "#e5e7eb" : "#0f172a",
  };
}

function TextField({
  label,
  value,
  onChange,
  mode,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  mode: "admin" | "client";
}) {
  return (
    <label
      style={{
        display: "grid",
        gap: 5,
        fontSize: 12,
        fontWeight: 850,
        color: mode === "admin" ? "#cbd5e1" : "#0f172a",
      }}
    >
      {label}
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Optional"
        style={fieldStyle(mode)}
      />
    </label>
  );
}

function SelectField({
  label,
  value,
  onChange,
  items,
  mode,
  suffix = "",
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  items: string[];
  mode: "admin" | "client";
  suffix?: string;
}) {
  return (
    <label
      style={{
        display: "grid",
        gap: 5,
        fontSize: 12,
        fontWeight: 850,
        color: mode === "admin" ? "#cbd5e1" : "#0f172a",
      }}
    >
      {label}
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        style={fieldStyle(mode)}
      >
        {items.map((item) => (
          <option key={item} value={item}>
            {item}
            {suffix && !String(item).endsWith(suffix) ? suffix : ""}
          </option>
        ))}
      </select>
    </label>
  );
}

export default function UniversalCompleteMediaRunAgentPanel({
  selectedAgent,
  selectedAgents,
  businessProfile,
  mode = "client",
  onConfigChange,
  onResult,
}: {
  selectedAgent?: string;
  selectedAgents?: string[];
  businessProfile?: BusinessProfile;
  mode?: "admin" | "client";
  onConfigChange?: (config: CompleteMediaConfig) => void;
  onResult?: (deliverable: any) => void;
}) {
  const portalMode: "admin" | "client" = mode === "admin" ? "admin" : "client";

  const [selectedPopupAgent, setSelectedPopupAgent] = useState("auto");
  const [selectedPopupAgents, setSelectedPopupAgents] = useState<string[]>(["ugc_creative_agent"]);

  const providedAgents = selectedAgents?.length
    ? selectedAgents
    : selectedAgent
      ? [selectedAgent]
      : [];

  const creativeAgents = providedAgents.filter(isCreativeAgent);
  const agents =
    creativeAgents.length > 0
      ? creativeAgents
      : portalMode === "admin"
        ? DEFAULT_CREATIVE_AGENTS
        : providedAgents.length > 0
          ? providedAgents
          : DEFAULT_CREATIVE_AGENTS.slice(0, 3);

  const autoSelectedCreativeAgent =
    agents.find(isCreativeAgent) || agents[0] || "ugc_creative_agent";

  const primaryAgent =
    selectedPopupAgent && selectedPopupAgent !== "auto"
      ? selectedPopupAgent
      : autoSelectedCreativeAgent;

  const shouldShow =
    portalMode === "admin" || agents.some(isCreativeAgent) || providedAgents.length === 0;

  const [popupOpen, setPopupOpen] = useState(false);
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [running, setRunning] = useState(false);
  const [statusMessage, setStatusMessage] = useState(
    "Ready. Click Create complete media now to run directly from this popup."
  );

  const [popupMediaJobId, setPopupMediaJobId] = useState("");
  const [popupMediaJobStatus, setPopupMediaJobStatus] = useState("");
  const [popupMediaPreviewUrl, setPopupMediaPreviewUrl] = useState("");
  const [popupMediaAssetUrl, setPopupMediaAssetUrl] = useState("");
  const [popupMediaFinalOutput, setPopupMediaFinalOutput] = useState("");


  const [prompt, setPrompt] = useState("");
  const [outputType, setOutputType] = useState("Complete video with voiceover");
  const [platform, setPlatform] = useState("General");
  const [durationSeconds, setDurationSeconds] = useState("5");
  const [aspectRatio, setAspectRatio] = useState("9:16");
  const [language, setLanguage] = useState("English");
  const [accent, setAccent] = useState("");
  const [tone, setTone] = useState("natural, polished, human");
  const [voiceStyle, setVoiceStyle] = useState("natural conversational voice");
  const [ageRange, setAgeRange] = useState("");
  const [genderPresentation, setGenderPresentation] = useState("");
  const [ethnicity, setEthnicity] = useState("");
  const [avatarLikeness, setAvatarLikeness] = useState("");
  const [facialFeatures, setFacialFeatures] = useState("");
  const [expressions, setExpressions] = useState("");
  const [gestures, setGestures] = useState("");
  const [wardrobe, setWardrobe] = useState("");
  const [backgroundSetting, setBackgroundSetting] = useState("");
  const [visualStyle, setVisualStyle] = useState("");
  const [cameraMovement, setCameraMovement] = useState("");
  const [musicStyle, setMusicStyle] = useState("");
  const [soundEffects, setSoundEffects] = useState("");
  const [callToAction, setCallToAction] = useState("");

  const profile = businessProfile || {};

  const mediaConfig: CompleteMediaConfig = useMemo(
    () => ({
      enabled: true,
      mode: portalMode,
      prompt,
      output_type: outputType,
      platform,
      duration_seconds: durationSeconds,
      aspect_ratio: aspectRatio,
      language,
      accent,
      tone,
      voice_style: voiceStyle,
      age_range: ageRange,
      gender_presentation: genderPresentation,
      ethnicity_or_cultural_appearance: ethnicity,
      avatar_likeness: avatarLikeness,
      facial_features: facialFeatures,
      expressions,
      gestures,
      wardrobe,
      background_setting: backgroundSetting,
      visual_style: visualStyle,
      camera_movement: cameraMovement,
      music_style: musicStyle,
      sound_effects: soundEffects,
      call_to_action: callToAction,
      agent_id: primaryAgent,
      selected_agent: primaryAgent,
      selected_agents: agents,
      industry: profile.business_niche || profile.industry || "",
      target_audience: profile.target_audience || "",
      brand_style: profile.brand_style || profile.brand_voice || profile.notes || "",
      product_or_service_details:
        profile.product_or_service_details ||
        profile.products_services ||
        profile.services ||
        "",
      speaking_pace: "natural, not rushed",
      lip_sync_accuracy: "high when avatar or talking-head output is requested",
      final_delivery_format: "mp4",
      run_direct_from_popup: true,
      native_popup_execution: true,
      creative_agent_direct_execution: true,
      requested_from: "complete_media_popup",
    }),
    [
      portalMode,
      prompt,
      outputType,
      platform,
      durationSeconds,
      aspectRatio,
      language,
      accent,
      tone,
      voiceStyle,
      ageRange,
      genderPresentation,
      ethnicity,
      avatarLikeness,
      facialFeatures,
      expressions,
      gestures,
      wardrobe,
      backgroundSetting,
      visualStyle,
      cameraMovement,
      musicStyle,
      soundEffects,
      callToAction,
      primaryAgent,
      selectedPopupAgent,
      agents,
      profile.business_niche,
      profile.industry,
      profile.target_audience,
      profile.brand_style,
      profile.brand_voice,
      profile.notes,
      profile.product_or_service_details,
      profile.products_services,
      profile.services,
    ]
  );

  useEffect(() => {
    onConfigChange?.(mediaConfig);

    try {
      window.localStorage.setItem(
        "universal_complete_media_config",
        JSON.stringify(mediaConfig)
      );

      window.dispatchEvent(
        new CustomEvent("universal-complete-media-config", {
          detail: mediaConfig,
        })
      );
    } catch {}
  }, [mediaConfig, onConfigChange]);

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem("universal_complete_media_config");
      if (!raw) return;

      const saved = JSON.parse(raw);
      if (saved?.prompt) setPrompt(String(saved.prompt));
      if (saved?.output_type) setOutputType(String(saved.output_type));
      if (saved?.platform) setPlatform(String(saved.platform));
      if (saved?.duration_seconds) setDurationSeconds(String(saved.duration_seconds));
      if (saved?.aspect_ratio) setAspectRatio(String(saved.aspect_ratio));
      if (saved?.language) setLanguage(String(saved.language));
      if (saved?.accent) setAccent(String(saved.accent));
      if (saved?.tone) setTone(String(saved.tone));
      if (saved?.voice_style) setVoiceStyle(String(saved.voice_style));
      if (saved?.call_to_action) setCallToAction(String(saved.call_to_action));
    } catch {}
  }, []);


  function resolvePopupSelectedAgents() {
    const availableCreativeAgents =
      agents.length > 0 ? agents : DEFAULT_CREATIVE_AGENTS;

    if (selectedPopupAgent === "auto") {
      const bestAgent =
        availableCreativeAgents.find(isCreativeAgent) ||
        availableCreativeAgents[0] ||
        "ugc_creative_agent";

      return [bestAgent];
    }

    if (selectedPopupAgent === "all") {
      const allCreativeAgents =
        availableCreativeAgents.filter(isCreativeAgent).length > 0
          ? availableCreativeAgents.filter(isCreativeAgent)
          : DEFAULT_CREATIVE_AGENTS;

      return Array.from(new Set(allCreativeAgents));
    }

    if (selectedPopupAgent === "custom") {
      const customAgents =
        selectedPopupAgents.length > 0
          ? selectedPopupAgents
          : ["ugc_creative_agent"];

      return Array.from(new Set(customAgents));
    }

    return [selectedPopupAgent || "ugc_creative_agent"];
  }

  function togglePopupAgent(agentId: string) {
    setSelectedPopupAgents((current) => {
      if (current.includes(agentId)) {
        const next = current.filter((agent) => agent !== agentId);
        return next.length > 0 ? next : ["ugc_creative_agent"];
      }

      return Array.from(new Set([...current, agentId]));
    });
  }


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

  async function runCompleteMediaFromPopup() {
    const cleanPrompt = String(prompt || "").trim();

    if (!cleanPrompt) {
      setStatusMessage("Add a media prompt first, then click Create complete media now.");
      return;
    }

    setRunning(true);

    const selectedCreativeAgents = resolvePopupSelectedAgents();
    const activeCreativeAgent = selectedCreativeAgents[0] || "ugc_creative_agent";
    const multiAgentMediaExecution = selectedCreativeAgents.length > 1;

    setStatusMessage(
      multiAgentMediaExecution
        ? `Creating complete media with ${selectedCreativeAgents.length} creative agents...`
        : `Creating complete media with ${activeCreativeAgent}...`
    );

    const directConfig = {
      ...mediaConfig,
      enabled: true,
      prompt: cleanPrompt,
      task: cleanPrompt,
      agent_id: activeCreativeAgent,
      selected_agent: activeCreativeAgent,
      selected_agents: selectedCreativeAgents,
      agent_ids: selectedCreativeAgents,
      requested_at: new Date().toISOString(),
      requested_from: "complete_media_popup",
      run_direct_from_popup: true,
      native_popup_execution: true,
      creative_agent_direct_execution: true,
      direct_media_provider_execute: true,
      multi_agent_media_execution: multiAgentMediaExecution,
      selected_agent_count: selectedCreativeAgents.length,
    };

    const provider =
      String(outputType || "").toLowerCase().includes("audio")
        ? "elevenlabs"
        : "runway";

    const mediaType =
      String(outputType || "").toLowerCase().includes("audio")
        ? "audio"
        : String(outputType || "").toLowerCase().includes("image")
          ? "image"
          : "video";

    const payload = {
      source: "complete_media_popup",
      requested_from: "complete_media_popup",
      portal_mode: portalMode,
      mode: portalMode,

      provider,
      provider_id: provider,
      media_type: mediaType,
      output_type: directConfig.output_type,
      platform: directConfig.platform,
      duration_seconds: directConfig.duration_seconds,
      aspect_ratio: directConfig.aspect_ratio,
      language: directConfig.language,
      accent: directConfig.accent,

      prompt: cleanPrompt,
      task: cleanPrompt,
      creative_brief: cleanPrompt,
      user_prompt: cleanPrompt,

      selected_agent: activeCreativeAgent,
      selected_agents: selectedCreativeAgents,
      agent_id: activeCreativeAgent,
      agent_ids: selectedCreativeAgents,
      lead_agent_id: activeCreativeAgent,

      business_profile: profile,
      complete_media_config: directConfig,
      media_config: directConfig,

      run_direct_from_popup: true,
      native_popup_execution: true,
      creative_agent_direct_execution: true,
      direct_media_provider_execute: true,
      multi_agent_media_execution: multiAgentMediaExecution,
      selected_agent_count: selectedCreativeAgents.length,

      customer_safe: portalMode !== "admin",
      owner_admin_unrestricted: portalMode === "admin",
    };

    try {
      window.localStorage.setItem(
        "universal_complete_media_config",
        JSON.stringify(directConfig)
      );
    } catch {}

    const endpoint =
      portalMode === "admin"
        ? "/api/admin-direct-media-provider-execute"
        : "/api/universal-complete-media";

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Portal-Mode": portalMode,
          "X-Requested-From": "complete_media_popup",
        },
        body: JSON.stringify(payload),
      });

      const result = await response.json().catch(() => ({
        success: false,
        error: "Invalid JSON response from direct media execution endpoint.",
      }));

      if (!response.ok || result?.success === false) {
        const errorText =
          result?.error ||
          result?.message ||
          result?.detail ||
          `Direct media request failed with HTTP ${response.status}.`;

        setStatusMessage(String(errorText));
        setRunning(false);
        return;
      }

      const extractedPopupResult = applyPopupMediaJobResult(result);

      const jobId =
        extractedPopupResult.jobId ||
        result?.media_job_id ||
        result?.job_id ||
        result?.provider_job_id ||
        result?.execution_id ||
        result?.request_id ||
        result?.id ||
        "";

      setStatusMessage(
        jobId
          ? `Complete media started from popup. Lead agent: ${activeCreativeAgent}. Agents: ${selectedCreativeAgents.length}. Job ID: ${jobId}`
          : `Complete media started from popup. Lead agent: ${activeCreativeAgent}. Agents: ${selectedCreativeAgents.length}.`
      );

      if (jobId) {
        setTimeout(() => {
          void checkPopupMediaJobStatus(jobId);
        }, 1200);
      }

      onResult?.(result);

      window.dispatchEvent(
        new CustomEvent("universal-complete-media-run-now", {
          detail: {
            endpoint,
            payload,
            result,
            native_popup_execution: true,
            selected_agent: activeCreativeAgent,
            selected_agents: selectedCreativeAgents,
            multi_agent_media_execution: multiAgentMediaExecution,
          },
        })
      );
    } catch (error) {
      setStatusMessage(
        error instanceof Error
          ? error.message
          : "Complete media popup execution failed."
      );
    } finally {
      setRunning(false);
    }
  }

  if (!shouldShow) return null;

  const statusLabel = "Direct complete media";

  return (
    <div
      data-run-agent-media-popup="true"
      data-mode={portalMode}
      data-true-direct-complete-media-popup="true"
      style={{ marginTop: 12 }}
    >
      <button
        type="button"
        onClick={() => setPopupOpen(true)}
        style={{
          border: "1px solid rgba(99,102,241,.35)",
          borderRadius: 999,
          padding: "9px 12px",
          background: "linear-gradient(135deg,rgba(79,70,229,.24),rgba(6,182,212,.18))",
          color: portalMode === "admin" ? "#c4b5fd" : "var(--color-brand, #4f46e5)",
          fontWeight: 950,
          cursor: "pointer",
          display: "inline-flex",
          alignItems: "center",
          gap: 8,
        }}
      >
        🎬 Media options
        <span style={{ opacity: 0.78, fontWeight: 800 }}>· {statusLabel}</span>
      </button>

      {popupOpen ? (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Create Media"
          onClick={() => setPopupOpen(false)}
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 2147483647,
            background: "rgba(2,6,23,.78)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 22,
          }}
        >
          <div
            onClick={(event) => event.stopPropagation()}
            style={{
              width: "min(920px,96vw)",
              maxHeight: "88vh",
              overflow: "auto",
              borderRadius: 24,
              border:
                portalMode === "admin"
                  ? "1px solid rgba(129,140,248,.3)"
                  : "1px solid rgba(226,232,240,.92)",
              background: portalMode === "admin" ? "#0f1228" : "#ffffff",
              boxShadow: "0 30px 90px rgba(0,0,0,.38)",
              padding: 20,
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                gap: 14,
                alignItems: "flex-start",
              }}
            >
              <div>
                <div
                  style={{
                    fontSize: 11,
                    fontWeight: 950,
                    letterSpacing: ".15em",
                    textTransform: "uppercase",
                    color: portalMode === "admin" ? "#818cf8" : "#4f46e5",
                  }}
                >
                  Create Media
                </div>
                <h3
                  style={{
                    margin: "6px 0 0",
                    color: portalMode === "admin" ? "#fff" : "#0f172a",
                  }}
                >
                  Create complete media
                </h3>
                <p
                  style={{
                    margin: "6px 0 0",
                    color: portalMode === "admin" ? "#94a3b8" : "#64748b",
                    fontSize: 13,
                    lineHeight: 1.5,
                  }}
                >
                  Choose one or more creative agents inside this popup, enter the media prompt, then click Create complete media now. You do not need to use the main Run Agent section.
                </p>
              </div>

              <button
                type="button"
                onClick={() => setPopupOpen(false)}
                style={{
                  border: "1px solid rgba(148,163,184,.32)",
                  background: portalMode === "admin" ? "rgba(15,23,42,.9)" : "#fff",
                  color: portalMode === "admin" ? "#e5e7eb" : "#334155",
                  borderRadius: 999,
                  padding: "8px 12px",
                  fontWeight: 850,
                  cursor: "pointer",
                }}
              >
                Close
              </button>
            </div>

            <div style={{ marginTop: 16, display: "grid", gap: 12 }}>
              <div
                data-complete-media-agent-selector="true"
                style={{
                  display: "grid",
                  gap: 10,
                  borderRadius: 16,
                  padding: 12,
                  border: "1px solid rgba(129,140,248,.22)",
                  background:
                    portalMode === "admin"
                      ? "rgba(15,23,42,.42)"
                      : "rgba(248,250,252,.9)",
                }}
              >
                <label
                  style={{
                    display: "grid",
                    gap: 6,
                    fontSize: 12.5,
                    fontWeight: 850,
                    color: portalMode === "admin" ? "#cbd5e1" : "#0f172a",
                  }}
                >
                  Agent selection mode
                  <select
                    value={selectedPopupAgent}
                    onChange={(event) => setSelectedPopupAgent(event.target.value)}
                    style={fieldStyle(portalMode)}
                  >
                    <option value="auto">Auto-select best creative agent</option>
                    <option value="all">Use all creative agents</option>
                    <option value="custom">Select multiple creative agents</option>
                    {POPUP_CREATIVE_AGENT_OPTIONS.filter((agent) => agent.value !== "auto").map((agent) => (
                      <option key={agent.value} value={agent.value}>
                        Single: {agent.label}
                      </option>
                    ))}
                  </select>
                </label>

                {selectedPopupAgent === "custom" ? (
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))",
                      gap: 8,
                    }}
                  >
                    {POPUP_CREATIVE_AGENT_OPTIONS.filter((agent) => agent.value !== "auto").map((agent) => (
                      <label
                        key={agent.value}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 8,
                          borderRadius: 12,
                          padding: "8px 10px",
                          border: "1px solid rgba(148,163,184,.24)",
                          color: portalMode === "admin" ? "#e5e7eb" : "#0f172a",
                          fontSize: 12.5,
                          fontWeight: 800,
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={selectedPopupAgents.includes(agent.value)}
                          onChange={() => togglePopupAgent(agent.value)}
                        />
                        {agent.label}
                      </label>
                    ))}
                  </div>
                ) : null}

                <div
                  style={{
                    color: portalMode === "admin" ? "#94a3b8" : "#64748b",
                    fontSize: 12,
                    lineHeight: 1.5,
                  }}
                >
                  Selected for this media run: {resolvePopupSelectedAgents().join(", ")}
                </div>
              </div>

              <label
                style={{
                  display: "grid",
                  gap: 6,
                  fontSize: 12.5,
                  fontWeight: 850,
                  color: portalMode === "admin" ? "#cbd5e1" : "#0f172a",
                }}
              >
                Media prompt
                <textarea
                  value={prompt}
                  onChange={(event) => setPrompt(event.target.value)}
                  placeholder="Describe the complete media file. Include the scene, presenter/avatar, voiceover, platform, tone, and final outcome."
                  style={{
                    minHeight: 120,
                    borderRadius: 16,
                    border: "1px solid rgba(148,163,184,.38)",
                    padding: 12,
                    fontSize: 13,
                    background: portalMode === "admin" ? "rgba(15,23,42,.92)" : "#fff",
                    color: portalMode === "admin" ? "#e5e7eb" : "#0f172a",
                  }}
                />
              </label>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit,minmax(170px,1fr))",
                  gap: 10,
                }}
              >
                <SelectField
                  label="Output type"
                  value={outputType}
                  onChange={setOutputType}
                  items={OUTPUT_TYPES}
                  mode={portalMode}
                />
                <SelectField
                  label="Platform"
                  value={platform}
                  onChange={setPlatform}
                  items={PLATFORMS}
                  mode={portalMode}
                />
                <SelectField
                  label="Duration"
                  value={durationSeconds}
                  onChange={setDurationSeconds}
                  items={DURATIONS}
                  mode={portalMode}
                  suffix="s"
                />
                <SelectField
                  label="Aspect ratio"
                  value={aspectRatio}
                  onChange={setAspectRatio}
                  items={ASPECT_RATIOS}
                  mode={portalMode}
                />
                <TextField
                  label="Language"
                  value={language}
                  onChange={setLanguage}
                  mode={portalMode}
                />
                <TextField
                  label="Accent"
                  value={accent}
                  onChange={setAccent}
                  mode={portalMode}
                />
              </div>

              <button
                type="button"
                onClick={() => setAdvancedOpen((value) => !value)}
                style={{
                  width: "fit-content",
                  border: "1px solid rgba(99,102,241,.28)",
                  borderRadius: 999,
                  padding: "9px 12px",
                  background: portalMode === "admin" ? "rgba(79,70,229,.14)" : "#fff",
                  color: portalMode === "admin" ? "#c4b5fd" : "#4f46e5",
                  fontWeight: 900,
                  cursor: "pointer",
                }}
              >
                {advancedOpen ? "Hide advanced media controls" : "Show advanced media controls"}
              </button>

              {advancedOpen ? (
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))",
                    gap: 10,
                  }}
                >
                  <TextField label="Tone" value={tone} onChange={setTone} mode={portalMode} />
                  <TextField label="Voice style" value={voiceStyle} onChange={setVoiceStyle} mode={portalMode} />
                  <TextField label="Age range" value={ageRange} onChange={setAgeRange} mode={portalMode} />
                  <TextField label="Gender presentation" value={genderPresentation} onChange={setGenderPresentation} mode={portalMode} />
                  <TextField label="Ethnicity / cultural appearance" value={ethnicity} onChange={setEthnicity} mode={portalMode} />
                  <TextField label="Ultra-human likeness" value={avatarLikeness} onChange={setAvatarLikeness} mode={portalMode} />
                  <TextField label="Facial features" value={facialFeatures} onChange={setFacialFeatures} mode={portalMode} />
                  <TextField label="Expressions" value={expressions} onChange={setExpressions} mode={portalMode} />
                  <TextField label="Gestures" value={gestures} onChange={setGestures} mode={portalMode} />
                  <TextField label="Wardrobe / styling" value={wardrobe} onChange={setWardrobe} mode={portalMode} />
                  <TextField label="Background / setting" value={backgroundSetting} onChange={setBackgroundSetting} mode={portalMode} />
                  <TextField label="Visual style" value={visualStyle} onChange={setVisualStyle} mode={portalMode} />
                  <TextField label="Camera movement" value={cameraMovement} onChange={setCameraMovement} mode={portalMode} />
                  <TextField label="Music style" value={musicStyle} onChange={setMusicStyle} mode={portalMode} />
                  <TextField label="Sound effects" value={soundEffects} onChange={setSoundEffects} mode={portalMode} />
                  <TextField label="Call-to-action" value={callToAction} onChange={setCallToAction} mode={portalMode} />
                </div>
              ) : null}

              <button
                type="button"
                data-complete-media-native-execution="true"
                disabled={running}
                onClick={runCompleteMediaFromPopup}
                style={{
                  width: "fit-content",
                  border: "1px solid rgba(34,197,94,.36)",
                  borderRadius: 999,
                  padding: "10px 14px",
                  background:
                    portalMode === "admin"
                      ? "linear-gradient(135deg, rgba(34,197,94,.24), rgba(6,182,212,.16))"
                      : "linear-gradient(135deg, rgba(34,197,94,.12), rgba(79,70,229,.10))",
                  color: portalMode === "admin" ? "#bbf7d0" : "#166534",
                  fontWeight: 950,
                  cursor: running ? "wait" : "pointer",
                  opacity: running ? 0.76 : 1,
                  boxShadow: "0 14px 34px rgba(15,23,42,.18)",
                }}
              >
                {running ? "Creating complete media..." : "Create complete media now"}
              </button>

              <div
                data-complete-media-popup-status="true"
                style={{
                  borderRadius: 16,
                  padding: 12,
                  background:
                    portalMode === "admin"
                      ? "rgba(79,70,229,.12)"
                      : "rgba(79,70,229,.07)",
                  color: portalMode === "admin" ? "#cbd5e1" : "#475569",
                  fontSize: 12.5,
                  lineHeight: 1.55,
                }}
              >
                {statusMessage}
              </div>

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
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
