from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "frontend" / "src" / "components" / "UniversalCompleteMediaRunAgentPanel.tsx"
BACKUP_DIR = ROOT / "backups" / f"true_direct_complete_media_popup_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if not TARGET.exists():
    raise SystemExit(f"TARGET_NOT_FOUND: {TARGET}")

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP_DIR / TARGET.name)

NEW_CONTENT = r'''"use client";

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
}: {
  selectedAgent?: string;
  selectedAgents?: string[];
  businessProfile?: BusinessProfile;
  mode?: "admin" | "client";
  onConfigChange?: (config: CompleteMediaConfig) => void;
}) {
  const portalMode: "admin" | "client" = mode === "admin" ? "admin" : "client";

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

  const primaryAgent =
    agents.find(isCreativeAgent) || agents[0] || "ugc_creative_agent";

  const shouldShow =
    portalMode === "admin" || agents.some(isCreativeAgent) || providedAgents.length === 0;

  const [popupOpen, setPopupOpen] = useState(false);
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [running, setRunning] = useState(false);
  const [statusMessage, setStatusMessage] = useState(
    "Ready. Click Create complete media now to run directly from this popup."
  );

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

  async function runCompleteMediaFromPopup() {
    setRunning(true);
    setStatusMessage("Creating complete media directly from this popup...");

    const directConfig = {
      ...mediaConfig,
      requested_at: new Date().toISOString(),
    };

    const endpoint =
      portalMode === "admin"
        ? "/api/admin-universal-complete-media"
        : "/api/universal-complete-media";

    const payload = {
      source: "complete_media_popup",
      requested_from: "complete_media_popup",
      portal_mode: portalMode,
      mode: portalMode,
      selected_agent: primaryAgent,
      selected_agents: agents,
      agent_id: primaryAgent,
      agent_ids: agents,
      business_profile: profile,
      complete_media_config: directConfig,
      media_config: directConfig,
      prompt: directConfig.prompt,
      task: directConfig.prompt,
      output_type: directConfig.output_type,
      platform: directConfig.platform,
      duration_seconds: directConfig.duration_seconds,
      aspect_ratio: directConfig.aspect_ratio,
      language: directConfig.language,
      accent: directConfig.accent,
      run_direct_from_popup: true,
      native_popup_execution: true,
      creative_agent_direct_execution: true,
      customer_safe: portalMode !== "admin",
      owner_admin_unrestricted: portalMode === "admin",
    };

    try {
      window.localStorage.setItem(
        "universal_complete_media_config",
        JSON.stringify(directConfig)
      );
    } catch {}

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
        error: "Invalid JSON response from complete media endpoint.",
      }));

      if (!response.ok || result?.success === false) {
        setStatusMessage(
          result?.error ||
            result?.message ||
            `Complete media request failed with HTTP ${response.status}.`
        );
        setRunning(false);
        return;
      }

      const jobId = result?.media_job_id || result?.job_id || result?.id || "";
      setStatusMessage(
        jobId
          ? `Complete media started directly from popup. Job ID: ${jobId}`
          : "Complete media started directly from popup."
      );

      window.dispatchEvent(
        new CustomEvent("universal-complete-media-run-now", {
          detail: {
            endpoint,
            payload,
            result,
            native_popup_execution: true,
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
          aria-label="Run Agent media options"
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
                  Run Agent media options
                </div>
                <h3
                  style={{
                    margin: "6px 0 0",
                    color: portalMode === "admin" ? "#fff" : "#0f172a",
                  }}
                >
                  Complete media output
                </h3>
                <p
                  style={{
                    margin: "6px 0 0",
                    color: portalMode === "admin" ? "#94a3b8" : "#64748b",
                    fontSize: 13,
                    lineHeight: 1.5,
                  }}
                >
                  Configure the media output here, then click Create complete media now. This runs directly from the popup without using the main Run Agent section.
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
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
'''

TARGET.write_text(NEW_CONTENT, encoding="utf-8")

verify = TARGET.read_text(encoding="utf-8")
required = [
    "data-true-direct-complete-media-popup",
    "data-complete-media-native-execution",
    "Create complete media now",
    "/api/admin-universal-complete-media",
    "/api/universal-complete-media",
    "This runs directly from the popup without using the main Run Agent section",
    "DEFAULT_CREATIVE_AGENTS",
]

missing = [item for item in required if item not in verify]
if missing:
    raise SystemExit(f"MISSING_REQUIRED_MARKERS: {missing}")

print("TRUE_DIRECT_COMPLETE_MEDIA_POPUP_REPLACED")
print(f"Backup folder: {BACKUP_DIR}")
print(f"Updated: {TARGET}")