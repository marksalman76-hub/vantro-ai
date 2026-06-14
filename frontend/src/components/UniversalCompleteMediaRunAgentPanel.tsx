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
  business_name: string;
  product_or_service: string;
  audience: string;
  goal: string;
  offer: string;
  must_include: string;
  must_avoid: string;
  human_avatar_mode: string;
  visual_references_assets: string;
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

const DURATIONS = ["5", "10", "15", "25", "30", "45", "60"];
const ASPECT_RATIOS = ["9:16", "1:1", "16:9", "4:5"];
const HUMAN_AVATAR_MODES = [
  "No human/avatar",
  "Generate new avatar/person",
  "Use client-uploaded face/likeness",
  "Use saved brand spokesperson/avatar",
];

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
  const [preflightResult, setPreflightResult] = useState<any>(null);
  const [technicalScriptPacketOpen, setTechnicalScriptPacketOpen] = useState(false);
  const [providerDiagnosticsOpen, setProviderDiagnosticsOpen] = useState(false);
  const [portalPayloadProviderCheck, setPortalPayloadProviderCheck] = useState("");


  const [prompt, setPrompt] = useState("");
  const [outputType, setOutputType] = useState("Complete video with voiceover");
  const [platform, setPlatform] = useState("General");
  const [durationSeconds, setDurationSeconds] = useState("25");
  const [aspectRatio, setAspectRatio] = useState("16:9");
  const [language, setLanguage] = useState("English");
  const [accent, setAccent] = useState("");
  const [tone, setTone] = useState("natural, polished, human");
  const [businessName, setBusinessName] = useState("");
  const [productOrService, setProductOrService] = useState("");
  const [audience, setAudience] = useState("");
  const [goal, setGoal] = useState("");
  const [offer, setOffer] = useState("");
  const [mustInclude, setMustInclude] = useState("");
  const [mustAvoid, setMustAvoid] = useState("");
  const [humanAvatarMode, setHumanAvatarMode] = useState("No human/avatar");
  const [visualReferencesAssets, setVisualReferencesAssets] = useState("");
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
      business_name: businessName,
      product_or_service: productOrService,
      audience,
      goal,
      offer,
      must_include: mustInclude,
      must_avoid: mustAvoid,
      human_avatar_mode: humanAvatarMode,
      visual_references_assets: visualReferencesAssets,
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
        productOrService ||
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
      businessName,
      productOrService,
      audience,
      goal,
      offer,
      mustInclude,
      mustAvoid,
      humanAvatarMode,
      visualReferencesAssets,
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
      if (saved?.business_name) setBusinessName(String(saved.business_name));
      if (saved?.product_or_service) setProductOrService(String(saved.product_or_service));
      if (saved?.audience) setAudience(String(saved.audience));
      if (saved?.goal) setGoal(String(saved.goal));
      if (saved?.offer) setOffer(String(saved.offer));
      if (saved?.must_include) setMustInclude(String(saved.must_include));
      if (saved?.must_avoid) setMustAvoid(String(saved.must_avoid));
      if (saved?.human_avatar_mode) setHumanAvatarMode(String(saved.human_avatar_mode));
      if (saved?.visual_references_assets) setVisualReferencesAssets(String(saved.visual_references_assets));
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

    const status = value?.status || value?.delivery_status || value?.composition_status || "ready";
    const url = extractPopupMediaUrl(value);
    return url
      ? `Final media output ${status}. Preview/open the generated asset above.`
      : `Final media output ${status}.`;
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

  function providerAttemptSummary(result: any) {
    const attempts = Array.isArray(result?.failed_provider_attempts)
      ? result.failed_provider_attempts
      : Array.isArray(result?.child_jobs?.visual_attempts)
        ? result.child_jobs.visual_attempts
        : [];

    if (!attempts.length) return "";

    return attempts
      .map((attempt: any) => {
        const provider = attempt?.provider || "provider";
        const status = attempt?.status || "failed";
        const summary = attempt?.safe_error_summary ? `: ${attempt.safe_error_summary}` : "";
        return `${provider} ${status}${summary}`;
      })
      .join(" | ");
  }

  function isProviderFailureResult(result: any) {
    const status = String(result?.status || extractPopupMediaStatus(result) || "").toLowerCase();
    return (
      status.includes("visual_failed") ||
      status.includes("provider_failed") ||
      status.includes("provider_execution_error") ||
      providerDiagnosticRows(result).length > 0
    );
  }

  function friendlyMediaStatus(status: any) {
    const value = String(status || "").toLowerCase();
    if (!value) return "Queued";
    if (value.includes("preflight_blocked")) return "Needs confirmation";
    if (value.includes("visual_failed") || value.includes("provider_failed") || value.includes("provider_execution_error")) {
      return "Provider needs attention";
    }
    if (value.includes("composition_failed") || value.includes("audio_failed") || value.includes("exception")) {
      return "Needs attention";
    }
    if (value.includes("complete")) return "Completed";
    if (value.includes("running") || value.includes("processing") || value.includes("progress")) return "Processing";
    if (value.includes("queued") || value.includes("received") || value.includes("pending")) return "Queued";
    if (value.includes("blocked")) return "Needs review";
    return String(status || "Queued").replace(/_/g, " ");
  }

  function friendlyProviderFailureMessage(result: any, segmentNote = "") {
    const counts = providerDiagnosticCounts(result);
    const attemptPhrase = counts.visualAttemptCount > 0
      ? `${counts.visualAttemptCount} visual provider attempt${counts.visualAttemptCount === 1 ? "" : "s"}`
      : "the visual provider attempt";
    return `Media generation needs provider attention.${segmentNote ? ` ${segmentNote}` : ""} No final asset was produced yet. ${attemptPhrase} did not complete. Open provider diagnostics for admin details, then retry a 5s media run when ready.`;
  }

  function providerDiagnosticRows(result: any) {
    const rawAttempts = [
      ...(Array.isArray(result?.failed_provider_attempts) ? result.failed_provider_attempts : []),
      ...(Array.isArray(result?.child_jobs?.visual_segments) ? result.child_jobs.visual_segments : []),
      ...(Array.isArray(result?.child_jobs?.visual_attempts) ? result.child_jobs.visual_attempts : []),
    ];
    const seen = new Set<string>();

    return rawAttempts
      .filter((attempt: any) => attempt && typeof attempt === "object")
      .map((attempt: any) => {
        const key = `${attempt?.provider || "provider"}-${attempt?.job_id || ""}-${attempt?.segment_index || ""}-${attempt?.status || ""}`;
        if (seen.has(key)) return null;
        seen.add(key);
        const provider = String(attempt?.provider || "provider");
        const providerJobId = String(attempt?.provider_job_id || "");
        const jobId = String(attempt?.job_id || "");
        const status = normaliseSegmentStatus(attempt?.status || "failed");
        const runwayCalled = provider.toLowerCase() === "runway" && Boolean(providerJobId || jobId || !String(attempt?.status || "").includes("blocked"));
        return {
          provider,
          status,
          jobId,
          providerJobId,
          runwayCalled,
          safeErrorSummary: String(attempt?.safe_error_summary || attempt?.reason || ""),
        };
      })
      .filter(Boolean);
  }

  function providerDiagnosticCounts(result: any) {
    const failedProviderAttempts = Array.isArray(result?.failed_provider_attempts)
      ? result.failed_provider_attempts
      : [];
    const visualAttempts = Array.isArray(result?.child_jobs?.visual_attempts)
      ? result.child_jobs.visual_attempts
      : [];
    const visualSegments = Array.isArray(result?.child_jobs?.visual_segments)
      ? result.child_jobs.visual_segments
      : [];
    return {
      providerAttemptCount: failedProviderAttempts.length || visualAttempts.length || visualSegments.length,
      visualAttemptCount: visualAttempts.length || visualSegments.length || failedProviderAttempts.filter((attempt: any) => String(attempt?.stage || "").includes("visual") || attempt?.segment_index).length,
      failedProviderAttemptCount: failedProviderAttempts.length,
    };
  }

  function canRetryMediaProviderFailure(result: any) {
    const status = String(result?.status || popupMediaJobStatus || "").toLowerCase();
    return portalMode === "admin" && (status.includes("visual_failed") || status.includes("provider_failed") || status.includes("provider_execution_error"));
  }

  function preflightSummary(result: any) {
    if (!result || typeof result !== "object") return "";
    const failedChecks = Array.isArray(result.failed_preflight_checks)
      ? result.failed_preflight_checks
      : [];
    const risk = result?.estimated_credit_risk?.risk_level;
    const visualCount = Array.isArray(result.executable_visual_providers)
      ? result.executable_visual_providers.length
      : 0;
    const audioCount = Array.isArray(result.executable_audio_providers)
      ? result.executable_audio_providers.length
      : 0;

    if (failedChecks.length > 0) {
      return `Preflight blocked: ${failedChecks.map((check: any) => check?.reason || check?.check).filter(Boolean).join(" | ")}`;
    }

    return `Preflight ready. Visual providers: ${visualCount}. Audio providers: ${audioCount}. Credit risk: ${risk || "unknown"}.`;
  }

  function isPaidMediaConfirmationRequired(result: any) {
    if (!result || typeof result !== "object") return false;
    const status = String(result?.status || "").toLowerCase();
    const failedChecks = Array.isArray(result?.failed_preflight_checks)
      ? result.failed_preflight_checks
      : [];
    const hasCreditRiskCheck = failedChecks.some((check: any) =>
      String(check?.check || check?.reason || "").toLowerCase().includes("estimated_credit_risk")
    );

    return (
      status === "universal_complete_media_preflight_blocked" ||
      status === "preflight_blocked" ||
      result?.estimated_credit_risk?.acceptable_without_confirmation === false ||
      hasCreditRiskCheck
    );
  }

  function paidMediaConfirmationSummary(result: any) {
    const requested = Number(result?.requested_duration_seconds || result?.estimated_duration_seconds || durationSeconds || 0);
    const segments = Number(result?.segment_count || 0);
    const visualCalls = Number(result?.estimated_credit_risk?.paid_visual_provider_attempts_possible || segments || 0);
    const audioCalls = Number(result?.estimated_credit_risk?.paid_audio_provider_attempts_possible || 1);
    const risk = String(result?.estimated_credit_risk?.risk_level || "unknown");

    return {
      requested,
      segments,
      visualCalls,
      audioCalls,
      risk,
    };
  }

  function normaliseSegmentStatus(status: any) {
    const value = String(status || "").toLowerCase();
    if (value.includes("complete")) return "completed";
    if (value.includes("fail") || value.includes("error")) return "failed";
    if (value.includes("run") || value.includes("process") || value.includes("progress")) return "running";
    if (value.includes("queue") || value.includes("plan")) return "queued";
    return value || "queued";
  }

  function segmentProgressRows(result: any) {
    const segmentCount = Number(result?.segment_count || 0);
    const planned = Array.isArray(result?.segment_plan) ? result.segment_plan : [];
    const generated = Array.isArray(result?.generated_segments) ? result.generated_segments : [];
    const childSegments = Array.isArray(result?.child_jobs?.visual_segments) ? result.child_jobs.visual_segments : [];
    const visualAttempts = Array.isArray(result?.child_jobs?.visual_attempts) ? result.child_jobs.visual_attempts : [];
    const missing = Array.isArray(result?.missing_segments) ? result.missing_segments.map((item: any) => Number(item)) : [];
    const total = segmentCount || planned.length || generated.length || childSegments.length || visualAttempts.length;

    return Array.from({ length: total }, (_, index) => {
      const segmentIndex = index + 1;
      const plannedSegment = planned.find((item: any) => Number(item?.segment_index) === segmentIndex) || {};
      const generatedSegment = generated.find((item: any) => Number(item?.segment_index) === segmentIndex);
      const childSegment = childSegments.find((item: any) => Number(item?.segment_index) === segmentIndex);
      const attemptSegment = visualAttempts.find((item: any) => Number(item?.segment_index) === segmentIndex);
      const matched = generatedSegment || childSegment || attemptSegment || plannedSegment;
      const status = generatedSegment
        ? "completed"
        : normaliseSegmentStatus(matched?.status || (missing.includes(segmentIndex) ? "queued" : "queued"));

      return {
        segmentIndex,
        total,
        status,
      };
    });
  }

  function audioProgressStatus(result: any) {
    return normaliseSegmentStatus(result?.audio_status || result?.child_jobs?.audio?.status || (result?.audio_job_id ? "completed" : "queued"));
  }

  function compositionProgressStatus(result: any) {
    return normaliseSegmentStatus(result?.composition_status || result?.child_jobs?.composition?.status || (result?.composition_job_id ? "completed" : "pending"));
  }

  async function checkPopupMediaJobStatus(jobIdOverride?: string) {
    const jobId = jobIdOverride || popupMediaJobId;

    if (!jobId) {
      setStatusMessage("No media job ID is available yet.");
      return;
    }

    const isUniversalCompleteMediaJob = String(jobId).startsWith("universal_complete_media_job_");

    const statusEndpoints =
      portalMode === "admin"
        ? [
            isUniversalCompleteMediaJob
              ? `/api/admin-universal-complete-media?job_id=${encodeURIComponent(jobId)}`
              : "",
            `/api/admin-direct-media-provider-job-status?job_id=${encodeURIComponent(jobId)}`,
          ].filter(Boolean)
        : [
            isUniversalCompleteMediaJob
              ? `/api/universal-complete-media-status?job_id=${encodeURIComponent(jobId)}`
              : `/api/universal-complete-media-status?job_id=${encodeURIComponent(jobId)}`,
          ];

    try {
      setStatusMessage(`Checking media job status for ${jobId}...`);

      let lastResult: any = null;
      let lastHttpStatus = 0;

      for (const statusEndpoint of statusEndpoints) {
        const response = await fetch(statusEndpoint, {
          method: "GET",
          headers: {
            "X-Portal-Mode": portalMode,
            "X-Requested-From": "complete_media_popup",
          },
          cache: "no-store",
        });

        lastHttpStatus = response.status;

        const result = await response.json().catch(() => ({
          success: false,
          error: "Invalid JSON response from media job status endpoint.",
          http_status: response.status,
        }));

        lastResult = result;

        const resultStatus = extractPopupMediaStatus(result);
        const resultJobId = extractPopupMediaJobId(result) || jobId;

        const acceptableUniversalStatus =
          isUniversalCompleteMediaJob &&
          [
            "queued",
            "received",
            "running",
            "running_visual_generation",
            "running_audio_generation",
            "running_synchronised_composition",
            "completed",
            "completed_duration_shortfall",
            "composition_duration_shortfall",
            "universal_complete_media_preflight_dry_run",
            "universal_complete_media_preflight_ready",
            "universal_complete_media_preflight_blocked",
            "universal_complete_media_visual_failed",
            "visual_failed_all_providers",
            "universal_complete_media_audio_failed",
            "universal_complete_media_composition_failed",
            "universal_complete_media_exception",
          ].includes(String(resultStatus || result?.status || "").trim());

        const statusRouteSucceeded =
          response.ok &&
          (
            result?.success === true ||
            result?.accepted === true ||
            Boolean(resultStatus) ||
            acceptableUniversalStatus ||
            result?.job_id === jobId ||
            result?.job_id === resultJobId
          );

        if (!statusRouteSucceeded) {
          continue;
        }

        const extracted = applyPopupMediaJobResult({
          ...result,
          job_id: resultJobId,
        });
        setPreflightResult(result);

        const status = extracted.status || resultStatus || result?.status || "status received";

        const segmentCount = Number(result?.segment_count || 0);
        const requestedDuration = Number(result?.requested_duration_seconds || result?.estimated_duration_seconds || 0);
        const generatedSegments = Array.isArray(result?.generated_segments) ? result.generated_segments.length : 0;
        const segmentNote = segmentCount > 0
          ? `${requestedDuration || durationSeconds}s requested -> ${segmentCount} visual segment${segmentCount === 1 ? "" : "s"}. Segment progress: ${generatedSegments}/${segmentCount}.`
          : "";
        const durationNote = result?.final_duration_seconds
          ? ` Final duration: ${Number(result.final_duration_seconds).toFixed(2)}s. Fulfilled: ${result?.duration_fulfilled === true ? "yes" : "no"}.`
          : "";
        setStatusMessage(
          isProviderFailureResult(result)
            ? friendlyProviderFailureMessage(result, segmentNote)
            : `Media job ${jobId} status: ${friendlyMediaStatus(status)}.${segmentNote ? ` ${segmentNote}` : ""}${durationNote}`
        );

        const terminalStatus = String(status || "").toLowerCase();
        if (
          terminalStatus === "completed" ||
          terminalStatus === "completed_duration_shortfall" ||
          terminalStatus === "composition_duration_shortfall" ||
          terminalStatus.includes("failed") ||
          terminalStatus.includes("exception") ||
          terminalStatus.includes("blocked")
        ) {
          setRunning(false);
        }

        return;
      }

      const fallbackStatus =
        extractPopupMediaStatus(lastResult) ||
        lastResult?.status ||
        "";

      if (isUniversalCompleteMediaJob && fallbackStatus) {
        applyPopupMediaJobResult({
          ...lastResult,
          job_id: jobId,
          status: fallbackStatus,
        });
        setStatusMessage(`Media job ${jobId} status: ${friendlyMediaStatus(fallbackStatus)}`);
        return;
      }

      setStatusMessage(
        lastResult?.error ||
          lastResult?.message ||
          lastResult?.reason ||
          `Media job status check returned HTTP ${lastHttpStatus || 200}, but the response did not match a supported job status shape.`
      );
    } catch (error) {
      setStatusMessage(
        error instanceof Error
          ? error.message
          : "Media job status check failed."
      );
    }
  }


  async function runCompleteMediaFromPopup(options: {
    dryRun?: boolean;
    smokeTest?: boolean;
    creditRiskAcknowledged?: boolean;
    useGeneratedScript?: boolean;
    confirmPaidMedia?: boolean;
  } = {}) {
    const cleanPrompt = String(prompt || "").trim();

    if (!cleanPrompt) {
      setStatusMessage("Add a media prompt first, then click Create complete media now.");
      return;
    }

    if (
      !options.dryRun &&
      !options.smokeTest &&
      !options.confirmPaidMedia &&
      isPaidMediaConfirmationRequired(preflightResult)
    ) {
      const summary = paidMediaConfirmationSummary(preflightResult);
      setStatusMessage(
        `${summary.requested || durationSeconds}s requested requires ${summary.segments || "multiple"} visual segment${summary.segments === 1 ? "" : "s"} and paid provider confirmation. No paid provider calls have started yet.`
      );
      return;
    }

    let creditRiskAcknowledged = Boolean(options.creditRiskAcknowledged || options.confirmPaidMedia);
    const preflightRisk = String(preflightResult?.estimated_credit_risk?.risk_level || "").toLowerCase();
    if (!options.dryRun && !options.smokeTest && preflightRisk === "high" && !creditRiskAcknowledged) {
      const confirmed = window.confirm(
        "This media run has a high estimated provider credit risk. Continue with paid provider execution?"
      );
      if (!confirmed) {
        setStatusMessage("Complete media run cancelled before paid provider execution.");
        return;
      }
      creditRiskAcknowledged = true;
    }

    setRunning(true);

    const selectedCreativeAgents = resolvePopupSelectedAgents();
    const activeCreativeAgent = selectedCreativeAgents[0] || "ugc_creative_agent";
    const multiAgentMediaExecution = selectedCreativeAgents.length > 1;

    setStatusMessage(
      options.dryRun
        ? "Checking media provider readiness..."
        : options.smokeTest
          ? `Running a labelled 5s smoke test with ${activeCreativeAgent}...`
          : multiAgentMediaExecution
        ? `Creating complete media with ${selectedCreativeAgents.length} creative agents...`
        : `Creating complete media with ${activeCreativeAgent}...`
    );

    const lowerPrompt = cleanPrompt.toLowerCase();
    const productRelevant =
      lowerPrompt.includes("product") ||
      lowerPrompt.includes("skincare") ||
      lowerPrompt.includes("cream") ||
      lowerPrompt.includes("serum") ||
      lowerPrompt.includes("bottle") ||
      lowerPrompt.includes("package") ||
      lowerPrompt.includes("packaging") ||
      lowerPrompt.includes("item") ||
      lowerPrompt.includes("using a") ||
      lowerPrompt.includes("holding a");

    const continuityGuardrails = [
      "Maintain consistent subjects, hands, faces, clothing, props, backgrounds, reflections, object positions, camera movement, and scene physics across the full clip.",
      "Avoid disappearing objects, morphing props, warped fingers, impossible reflections, mismatched hand movement, sudden object teleporting, or visual continuity breaks.",
      "Keep physical interactions realistic and temporally consistent.",
      "When voiceover or narration is requested, pace the visual action so it can align naturally with the spoken script.",
      productRelevant
        ? "Because this prompt involves a product or handled object, keep the product visible and visually consistent, maintain accurate hand-product contact, and keep mirror/reflection placement consistent when reflections appear."
        : "",
    ]
      .filter(Boolean)
      .join(" ");

    const directConfig = {
      ...mediaConfig,
      enabled: true,
      prompt: cleanPrompt,
      media_prompt: cleanPrompt,
      task: cleanPrompt,
      visual_quality_guardrails: continuityGuardrails,
      agent_id: activeCreativeAgent,
      selected_agent: activeCreativeAgent,
      selected_agents: selectedCreativeAgents,
      agent_ids: selectedCreativeAgents,
      media_type: "complete_video",
      asset_type: "video",
      output_type: outputType,
      duration_seconds: options.smokeTest ? "5" : durationSeconds,
      aspect_ratio: aspectRatio,
      video_provider: "runway",
      audio_provider: "elevenlabs",
      requested_at: new Date().toISOString(),
      requested_from: "complete_media_popup",
      run_direct_from_popup: true,
      native_popup_execution: true,
      creative_agent_direct_execution: true,
      universal_complete_media_workflow: true,
      one_prompt_complete_media: true,
      multi_agent_media_execution: multiAgentMediaExecution,
      selected_agent_count: selectedCreativeAgents.length,
      dry_run: Boolean(options.dryRun),
      preflight_only: Boolean(options.dryRun),
      check_readiness: Boolean(options.dryRun),
      smoke_test_mode: Boolean(options.smokeTest),
      smoke_test_label: options.smokeTest ? "5s smoke test" : "",
      credit_risk_acknowledged: creditRiskAcknowledged,
      cost_safety_confirmed: Boolean(options.confirmPaidMedia),
      paid_provider_risk_confirmed: Boolean(options.confirmPaidMedia),
      use_generated_script: Boolean(options.useGeneratedScript),
      script_approved: Boolean(options.useGeneratedScript),
    };

    const payload = {
      source: "complete_media_popup",
      requested_from: "complete_media_popup",
      portal_mode: portalMode,
      mode: portalMode,

      prompt: cleanPrompt,
      media_prompt: cleanPrompt,
      task: cleanPrompt,
      creative_brief: cleanPrompt,
      user_prompt: cleanPrompt,
      visual_quality_guardrails: continuityGuardrails,

      selected_agent: activeCreativeAgent,
      selected_agents: selectedCreativeAgents,
      agent_id: activeCreativeAgent,
      agent_ids: selectedCreativeAgents,
      lead_agent_id: activeCreativeAgent,

      business_profile: profile,
      complete_media_config: directConfig,
      media_config: directConfig,

      output_type: directConfig.output_type || outputType,
      platform: directConfig.platform || platform,
      duration_seconds: options.smokeTest ? "5" : directConfig.duration_seconds || durationSeconds,
      aspect_ratio: directConfig.aspect_ratio || aspectRatio,
      language: directConfig.language || language,
      accent: directConfig.accent || accent,
      tone: directConfig.tone,
      business_name: directConfig.business_name,
      product_or_service: directConfig.product_or_service,
      audience: directConfig.audience,
      goal: directConfig.goal,
      offer: directConfig.offer,
      must_include: directConfig.must_include,
      must_avoid: directConfig.must_avoid,
      human_avatar_mode: directConfig.human_avatar_mode,
      visual_references_assets: directConfig.visual_references_assets,
      voice_style: directConfig.voice_style,
      call_to_action: directConfig.call_to_action,
      use_generated_script: Boolean(options.useGeneratedScript),
      script_approved: Boolean(options.useGeneratedScript),

      video_provider: "runway",
      audio_provider: "elevenlabs",
      provider: "universal_complete_media_workflow",
      media_type: "complete_video",
      asset_type: "video",

      run_direct_from_popup: true,
      native_popup_execution: true,
      creative_agent_direct_execution: true,
      universal_complete_media_workflow: true,
      one_prompt_complete_media: true,
      multi_agent_media_execution: multiAgentMediaExecution,
      selected_agent_count: selectedCreativeAgents.length,
      dry_run: Boolean(options.dryRun),
      preflight_only: Boolean(options.dryRun),
      check_readiness: Boolean(options.dryRun),
      smoke_test_mode: Boolean(options.smokeTest),
      smoke_test_label: options.smokeTest ? "5s smoke test" : "",
      credit_risk_acknowledged: creditRiskAcknowledged,
      cost_safety_confirmed: Boolean(options.confirmPaidMedia),
      paid_provider_risk_confirmed: Boolean(options.confirmPaidMedia),

      owner_approved: portalMode === "admin",
      owner_approval_granted: portalMode === "admin",
      customer_safe: portalMode !== "admin",
      owner_admin_unrestricted: portalMode === "admin",
    };

    setPortalPayloadProviderCheck(
      `Portal payload provider check: video_provider=${payload.video_provider}, audio_provider=${payload.audio_provider}, duration=${payload.duration_seconds}, dry_run=${String(payload.dry_run)}, preflight_only=${String(payload.preflight_only)}`
    );

    try {
      window.localStorage.setItem(
        "universal_complete_media_config",
        JSON.stringify(directConfig)
      );
    } catch {}

    const endpoint =
      portalMode === "admin"
        ? "/api/admin-universal-complete-media"
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
        error: "Invalid JSON response from universal complete media endpoint.",
      }));

      if (response.ok && result?.success === false && isPaidMediaConfirmationRequired(result)) {
        applyPopupMediaJobResult(result);
        setPreflightResult(result);
        const summary = paidMediaConfirmationSummary(result);
        setStatusMessage(
          `${summary.requested || durationSeconds}s requested requires paid provider confirmation: ${summary.visualCalls} Runway visual call${summary.visualCalls === 1 ? "" : "s"} + ${summary.audioCalls} ElevenLabs audio call${summary.audioCalls === 1 ? "" : "s"}. No paid provider calls have started yet.`
        );
        setRunning(false);
        onResult?.(result);
        window.dispatchEvent(
          new CustomEvent("universal-complete-media-run-now", {
            detail: {
              endpoint,
              payload,
              result,
              native_popup_execution: true,
              confirmation_required: true,
              selected_agent: activeCreativeAgent,
              selected_agents: selectedCreativeAgents,
              multi_agent_media_execution: multiAgentMediaExecution,
              universal_complete_media_workflow: true,
            },
          })
        );
        return;
      }

      const resultStatus = String(result?.status || "");
      const providerFailureResult =
        response.ok &&
        result?.success === false &&
        isProviderFailureResult(result);

      if (providerFailureResult) {
        const extracted = applyPopupMediaJobResult(result);
        setPreflightResult(result);
        const segmentCount = Number(result?.segment_count || 0);
        const requestedDuration = Number(result?.requested_duration_seconds || result?.estimated_duration_seconds || durationSeconds || 0);
        const generatedSegments = Array.isArray(result?.generated_segments) ? result.generated_segments.length : 0;
        const segmentNote = segmentCount > 0
          ? `${requestedDuration || durationSeconds}s requested -> ${segmentCount} visual segment${segmentCount === 1 ? "" : "s"}. Segment progress: ${generatedSegments}/${segmentCount}.`
          : "Provider execution stopped before a final asset was produced.";
        setStatusMessage(friendlyProviderFailureMessage(result, `${segmentNote}${extracted.jobId ? ` Job ID: ${extracted.jobId}.` : ""}`));
        setRunning(false);
        onResult?.(result);
        return;
      }

      if (!response.ok || result?.success === false) {
        const errorText =
          result?.error ||
          result?.message ||
          result?.detail ||
          `Universal complete media request returned status ${response.status}.`;

        setStatusMessage(String(errorText));
        setRunning(false);
        return;
      }

      const extractedPopupResult = applyPopupMediaJobResult(result);
      if (
        options.dryRun ||
        result?.status === "universal_complete_media_preflight_blocked" ||
        result?.status === "universal_complete_media_preflight_dry_run" ||
        result?.estimated_credit_risk
      ) {
        setPreflightResult(result);
      }

      const jobId =
        extractedPopupResult.jobId ||
        result?.media_job_id ||
        result?.job_id ||
        result?.provider_job_id ||
        result?.execution_id ||
        result?.request_id ||
        result?.id ||
        "";

      if (options.dryRun || resultStatus.includes("preflight")) {
        setStatusMessage(
          `${preflightSummary(result) || result?.message || "Preflight completed."}${jobId ? ` Job ID: ${jobId}` : ""}`
        );
      } else {
        setStatusMessage(
          jobId
            ? `Complete media workflow started. Lead agent: ${activeCreativeAgent}. Agents: ${selectedCreativeAgents.length}. Job ID: ${jobId}`
            : `Complete media workflow started. Lead agent: ${activeCreativeAgent}. Agents: ${selectedCreativeAgents.length}.`
        );
      }

      if (jobId && !options.dryRun && !resultStatus.includes("preflight")) {
        setTimeout(() => {
          void checkPopupMediaJobStatus(jobId);
        }, 1500);
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
            universal_complete_media_workflow: true,
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
                <TextField
                  label="Business name"
                  value={businessName}
                  onChange={setBusinessName}
                  mode={portalMode}
                />
                <TextField
                  label="Product or service"
                  value={productOrService}
                  onChange={setProductOrService}
                  mode={portalMode}
                />
                <TextField
                  label="Audience"
                  value={audience}
                  onChange={setAudience}
                  mode={portalMode}
                />
                <TextField
                  label="Goal"
                  value={goal}
                  onChange={setGoal}
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
                  <TextField label="Offer" value={offer} onChange={setOffer} mode={portalMode} />
                  <TextField label="Must include" value={mustInclude} onChange={setMustInclude} mode={portalMode} />
                  <TextField label="Must avoid" value={mustAvoid} onChange={setMustAvoid} mode={portalMode} />
                  <SelectField
                    label="Human/avatar mode"
                    value={humanAvatarMode}
                    onChange={setHumanAvatarMode}
                    items={HUMAN_AVATAR_MODES}
                    mode={portalMode}
                  />
                  <TextField label="Visual references/assets" value={visualReferencesAssets} onChange={setVisualReferencesAssets} mode={portalMode} />
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

              <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                <button
                  type="button"
                  data-complete-media-readiness-check="true"
                  disabled={running}
                  onClick={() => void runCompleteMediaFromPopup({ dryRun: true })}
                  style={{
                    width: "fit-content",
                    border: "1px solid rgba(59,130,246,.34)",
                    borderRadius: 999,
                    padding: "10px 14px",
                    background: portalMode === "admin" ? "rgba(59,130,246,.14)" : "#fff",
                    color: portalMode === "admin" ? "#bfdbfe" : "#1d4ed8",
                    fontWeight: 950,
                    cursor: running ? "wait" : "pointer",
                    opacity: running ? 0.76 : 1,
                  }}
                >
                  Check readiness
                </button>

                <button
                  type="button"
                  data-complete-media-smoke-test="true"
                  disabled={running}
                  onClick={() => void runCompleteMediaFromPopup({ smokeTest: true })}
                  style={{
                    width: "fit-content",
                    border: "1px solid rgba(245,158,11,.36)",
                    borderRadius: 999,
                    padding: "10px 14px",
                    background: portalMode === "admin" ? "rgba(245,158,11,.14)" : "#fff",
                    color: portalMode === "admin" ? "#fde68a" : "#92400e",
                    fontWeight: 950,
                    cursor: running ? "wait" : "pointer",
                    opacity: running ? 0.76 : 1,
                  }}
                >
                  Run 5s smoke test
                </button>

                <button
                  type="button"
                  data-complete-media-native-execution="true"
                  disabled={running || preflightResult?.status === "universal_complete_media_preflight_blocked"}
                  onClick={() => void runCompleteMediaFromPopup()}
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
                    cursor: running ? "wait" : preflightResult?.status === "universal_complete_media_preflight_blocked" ? "not-allowed" : "pointer",
                    opacity: running || preflightResult?.status === "universal_complete_media_preflight_blocked" ? 0.62 : 1,
                    boxShadow: "0 14px 34px rgba(15,23,42,.18)",
                  }}
                >
                  {running ? "Creating complete media..." : "Create complete media now"}
                </button>
              </div>

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
                {portalMode === "admin" && portalPayloadProviderCheck ? (
                  <div
                    data-complete-media-payload-provider-check="true"
                    style={{
                      marginTop: 8,
                      paddingTop: 8,
                      borderTop: "1px solid rgba(148,163,184,.22)",
                      color: "#bfdbfe",
                      fontWeight: 850,
                    }}
                  >
                    {portalPayloadProviderCheck}
                  </div>
                ) : null}
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
                {portalMode === "admin" ? (
                  <div
                    data-complete-media-popup-ux-version="v3"
                    style={{
                      width: "fit-content",
                      borderRadius: 999,
                      padding: "4px 8px",
                      background: "rgba(59,130,246,.14)",
                      color: "#bfdbfe",
                      fontSize: 11,
                      fontWeight: 950,
                    }}
                  >
                    Complete media popup UX v3
                  </div>
                ) : null}
                <div style={{ fontWeight: 950 }}>Media job result</div>

                {popupMediaJobId ? (
                  <div>
                    <strong>Job ID:</strong> {popupMediaJobId}
                  </div>
                ) : null}

                {popupMediaJobStatus ? (
                  <div>
                    <strong>Status:</strong> {friendlyMediaStatus(popupMediaJobStatus)}
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

                {portalMode === "admin" && isPaidMediaConfirmationRequired(preflightResult) ? (
                  <div
                    data-complete-media-paid-confirmation-required="true"
                    style={{
                      display: "grid",
                      gap: 10,
                      borderRadius: 14,
                      padding: 12,
                      border: "1px solid rgba(245,158,11,.34)",
                      background: "rgba(245,158,11,.12)",
                      color: "#fde68a",
                    }}
                  >
                    <strong>Paid provider confirmation required</strong>
                    {(() => {
                      const summary = paidMediaConfirmationSummary(preflightResult);
                      return (
                        <>
                          <div>
                            {summary.requested || durationSeconds}s requested {"->"} {summary.segments || preflightResult?.segment_count || 0} visual segment{Number(summary.segments || preflightResult?.segment_count || 0) === 1 ? "" : "s"}
                          </div>
                          <div>
                            Estimated paid calls: {summary.visualCalls} Runway visual call{summary.visualCalls === 1 ? "" : "s"} + {summary.audioCalls} ElevenLabs audio call{summary.audioCalls === 1 ? "" : "s"}
                          </div>
                          <div>Risk level: {summary.risk}</div>
                          <div>No paid provider calls have started yet</div>
                        </>
                      );
                    })()}
                    <button
                      type="button"
                      data-complete-media-confirm-paid-run="true"
                      disabled={running}
                      onClick={() => void runCompleteMediaFromPopup({ confirmPaidMedia: true })}
                      style={{
                        width: "fit-content",
                        border: "1px solid rgba(34,197,94,.42)",
                        borderRadius: 999,
                        padding: "9px 13px",
                        background: "rgba(34,197,94,.18)",
                        color: "#bbf7d0",
                        fontWeight: 950,
                        cursor: running ? "wait" : "pointer",
                      }}
                    >
                      Confirm and run paid media
                    </button>
                  </div>
                ) : null}

                {preflightResult?.segment_count ? (
                  <div
                    data-complete-media-segment-progress="true"
                    style={{
                      display: "grid",
                      gap: 8,
                      borderRadius: 14,
                      padding: 10,
                      background:
                        portalMode === "admin"
                          ? "rgba(20,184,166,.10)"
                          : "rgba(240,253,250,.9)",
                      color: portalMode === "admin" ? "#ccfbf1" : "#134e4a",
                    }}
                  >
                    <strong>
                      {preflightResult.requested_duration_seconds || durationSeconds}s requested {"->"} {preflightResult.segment_count} visual segment{Number(preflightResult.segment_count) === 1 ? "" : "s"}
                    </strong>
                    <div style={{ opacity: 0.92 }}>
                      This can take several minutes because each 5-second visual segment is generated separately, then stitched with voiceover into one final video.
                    </div>
                    {segmentProgressRows(preflightResult).length > 0 ? (
                      <div style={{ display: "grid", gap: 6 }}>
                        {segmentProgressRows(preflightResult).map((segment) => (
                          <div
                            key={segment.segmentIndex}
                            data-complete-media-segment-row="true"
                            style={{
                              display: "flex",
                              justifyContent: "space-between",
                              gap: 10,
                              borderRadius: 10,
                              padding: "7px 9px",
                              background: portalMode === "admin" ? "rgba(15,23,42,.36)" : "rgba(255,255,255,.74)",
                            }}
                          >
                            <span>Segment {segment.segmentIndex} of {segment.total}</span>
                            <strong>{segment.status}</strong>
                          </div>
                        ))}
                      </div>
                    ) : null}
                    <div style={{ display: "grid", gap: 6 }}>
                      <div
                        data-complete-media-audio-row="true"
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          gap: 10,
                          borderRadius: 10,
                          padding: "7px 9px",
                          background: portalMode === "admin" ? "rgba(15,23,42,.36)" : "rgba(255,255,255,.74)",
                        }}
                      >
                        <span>Voiceover</span>
                        <strong>{audioProgressStatus(preflightResult)}</strong>
                      </div>
                      <div
                        data-complete-media-composition-row="true"
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          gap: 10,
                          borderRadius: 10,
                          padding: "7px 9px",
                          background: portalMode === "admin" ? "rgba(15,23,42,.36)" : "rgba(255,255,255,.74)",
                        }}
                      >
                        <span>Composition</span>
                        <strong>{compositionProgressStatus(preflightResult)}</strong>
                      </div>
                    </div>
                    {preflightResult.final_duration_seconds ? (
                      <div>
                        <strong>Final duration:</strong> {Number(preflightResult.final_duration_seconds).toFixed(2)}s
                        {" - "}
                        <strong>Duration fulfilled:</strong> {preflightResult.duration_fulfilled === true ? "true" : "false"}
                        {Number(preflightResult.duration_shortfall_seconds || 0) > 0 ? ` - Shortfall: ${Number(preflightResult.duration_shortfall_seconds).toFixed(2)}s` : ""}
                      </div>
                    ) : null}
                  </div>
                ) : null}

                {portalMode === "admin" && providerDiagnosticRows(preflightResult).length > 0 ? (
                  <div
                    data-complete-media-provider-diagnostics-summary="true"
                    style={{
                      display: "grid",
                      gap: 8,
                      borderRadius: 14,
                      padding: 10,
                      background: "rgba(239,68,68,.10)",
                      color: "#fecaca",
                      border: "1px solid rgba(239,68,68,.28)",
                    }}
                  >
                    <strong>Visual generation needs attention</strong>
                    <div>No final media asset was produced yet. Admin diagnostics are available if you need the provider attempt details.</div>
                    <button
                      type="button"
                      data-complete-media-provider-diagnostics-toggle="true"
                      onClick={() => setProviderDiagnosticsOpen((value) => !value)}
                      style={{
                        width: "fit-content",
                        border: "1px solid rgba(248,113,113,.38)",
                        borderRadius: 999,
                        padding: "8px 12px",
                        background: "rgba(248,113,113,.12)",
                        color: "#fecaca",
                        fontWeight: 950,
                        cursor: "pointer",
                      }}
                    >
                      {providerDiagnosticsOpen ? "Hide provider diagnostics" : "Show provider diagnostics"}
                    </button>
                    {providerDiagnosticsOpen ? (
                      <div data-complete-media-provider-diagnostics="true" style={{ display: "grid", gap: 8 }}>
                        <strong>Provider attempt details</strong>
                        {(() => {
                          const counts = providerDiagnosticCounts(preflightResult);
                          return (
                            <div
                              data-complete-media-provider-attempt-counts="true"
                              style={{
                                display: "grid",
                                gap: 3,
                                borderRadius: 10,
                                padding: "8px 9px",
                                background: "rgba(15,23,42,.28)",
                              }}
                            >
                              <div>provider_attempt_count: {counts.providerAttemptCount}</div>
                              <div>visual_attempt_count: {counts.visualAttemptCount}</div>
                              <div>failed_provider_attempts: {counts.failedProviderAttemptCount}</div>
                            </div>
                          );
                        })()}
                        {providerDiagnosticRows(preflightResult).map((attempt: any, index: number) => (
                          <div
                            key={`${attempt.provider}-${attempt.jobId}-${index}`}
                            style={{
                              display: "grid",
                              gap: 3,
                              borderRadius: 10,
                              padding: "8px 9px",
                              background: "rgba(15,23,42,.38)",
                            }}
                          >
                            <div>
                              <strong>{attempt.provider}</strong> {attempt.status}
                            </div>
                            <div>Runway called: {attempt.provider.toLowerCase() === "runway" ? (attempt.runwayCalled ? "yes" : "no") : "not applicable"}</div>
                            {attempt.providerJobId ? <div>Provider job ID: {attempt.providerJobId}</div> : null}
                            {attempt.jobId ? <div>Child job ID: {attempt.jobId}</div> : null}
                            {attempt.safeErrorSummary ? <div>Safe error summary: {attempt.safeErrorSummary}</div> : null}
                          </div>
                        ))}
                      </div>
                    ) : null}
                    {canRetryMediaProviderFailure(preflightResult) ? (
                      <button
                        type="button"
                        data-complete-media-retry-provider-failure="true"
                        disabled={running}
                        onClick={() => void runCompleteMediaFromPopup({ smokeTest: true, creditRiskAcknowledged: true })}
                        style={{
                          width: "fit-content",
                          border: "1px solid rgba(248,113,113,.38)",
                          borderRadius: 999,
                          padding: "8px 12px",
                          background: "rgba(248,113,113,.14)",
                          color: "#fecaca",
                          fontWeight: 950,
                          cursor: running ? "wait" : "pointer",
                        }}
                      >
                        Retry 5s media
                      </button>
                    ) : null}
                  </div>
                ) : null}

                {preflightResult?.media_script_preview ? (
                  <div
                    data-complete-media-script-preview="true"
                    style={{
                      display: "grid",
                      gap: 8,
                      borderRadius: 14,
                      padding: 10,
                      background:
                        portalMode === "admin"
                          ? "rgba(59,130,246,.10)"
                          : "rgba(239,246,255,.9)",
                      color: portalMode === "admin" ? "#dbeafe" : "#1e3a8a",
                    }}
                  >
                    <strong>Generated media plan</strong>
                    {preflightResult.media_script_preview.voiceover_script ? (
                      <div>
                        <strong>Voiceover:</strong> {preflightResult.media_script_preview.voiceover_script}
                      </div>
                    ) : null}
                    <div>
                      <strong>Scene count:</strong> {preflightResult.media_script_preview.scene_count || 0}
                      {" - "}
                      <strong>Script fit:</strong> {preflightResult.media_script_preview.script_duration_fit || "unknown"}
                    </div>
                    {preflightResult.media_script_preview.cta_text ? (
                      <div>
                        <strong>CTA:</strong> {preflightResult.media_script_preview.cta_text}
                      </div>
                    ) : null}
                    {Array.isArray(preflightResult.media_script_preview.caption_plan) && preflightResult.media_script_preview.caption_plan.length > 0 ? (
                      <div>
                        <strong>Captions:</strong>
                        <div style={{ display: "grid", gap: 4, marginTop: 4 }}>
                          {preflightResult.media_script_preview.caption_plan.slice(0, 6).map((caption: any, index: number) => (
                            <div key={`${caption?.start || index}-${caption?.caption_text || index}`}>
                              {index + 1}. {String(caption?.caption_text || caption || "")}
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : null}
                    <div>
                      <strong>Human/avatar mode:</strong> {preflightResult.media_script_packet?.inferred_business_context?.human_avatar_mode || humanAvatarMode || "Not specified"}
                    </div>
                    <div>
                      <strong>Selected creative agent(s):</strong> {(preflightResult.media_script_packet?.contributing_agents || resolvePopupSelectedAgents()).join(", ")}
                    </div>
                    {portalMode === "admin" && preflightResult?.media_script_packet ? (
                      <>
                        <button
                          type="button"
                          onClick={() => void runCompleteMediaFromPopup({ useGeneratedScript: true })}
                          disabled={running}
                          style={{
                            width: "fit-content",
                            border: "1px solid rgba(34,197,94,.34)",
                            borderRadius: 999,
                            padding: "8px 12px",
                            background: "rgba(34,197,94,.13)",
                            color: "#bbf7d0",
                            fontWeight: 900,
                            cursor: running ? "wait" : "pointer",
                          }}
                        >
                          Use generated script
                        </button>
                        <button
                          type="button"
                          data-complete-media-technical-script-toggle="true"
                          onClick={() => setTechnicalScriptPacketOpen((value) => !value)}
                          style={{
                            width: "fit-content",
                            border: "1px solid rgba(148,163,184,.34)",
                            borderRadius: 999,
                            padding: "8px 12px",
                            background: "rgba(148,163,184,.12)",
                            color: portalMode === "admin" ? "#e5e7eb" : "#334155",
                            fontWeight: 900,
                            cursor: "pointer",
                          }}
                        >
                          {technicalScriptPacketOpen ? "Hide technical script packet" : "Show technical script packet"}
                        </button>
                        {technicalScriptPacketOpen ? (
                          <pre
                            data-complete-media-technical-script-packet="true"
                            style={{
                              whiteSpace: "pre-wrap",
                              overflow: "auto",
                              maxHeight: 260,
                              borderRadius: 12,
                              padding: 10,
                              background: "rgba(2,6,23,.74)",
                              color: "#e5e7eb",
                            }}
                          >
                            {JSON.stringify(preflightResult.media_script_packet, null, 2)}
                          </pre>
                        ) : null}
                      </>
                    ) : null}
                  </div>
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
