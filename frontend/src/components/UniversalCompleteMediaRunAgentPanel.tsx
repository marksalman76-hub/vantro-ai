"use client";

import React, { useEffect, useMemo, useState } from "react";

type UniversalCompleteMediaRunAgentPanelProps = {
  selectedAgent?: string;
  selectedAgents?: string[];
  businessProfile?: Record<string, string>;
  mode?: "client" | "admin";
  onResult?: (deliverable: Record<string, unknown>) => void;
  onConfigChange?: (config: Record<string, unknown>) => void;
};

const outputTypes = [
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

const platforms = [
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

const durations = ["5", "10", "15", "30", "45", "60"];
const aspectRatios = ["9:16", "1:1", "16:9", "4:5"];

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
];

function isCreativeCapableAgent(agentId: string) {
  const value = String(agentId || "").toLowerCase();
  return CREATIVE_AGENT_KEYWORDS.some((keyword) => value.includes(keyword));
}

function readStoredConfig() {
  try {
    const stored = window.localStorage.getItem("universal_complete_media_config");
    return stored ? JSON.parse(stored) : {};
  } catch {
    return {};
  }
}

export default function UniversalCompleteMediaRunAgentPanel({
  selectedAgent,
  selectedAgents,
  businessProfile,
  mode = "client",
  onConfigChange,
}: UniversalCompleteMediaRunAgentPanelProps) {
  const activeAgents = selectedAgents?.length ? selectedAgents : selectedAgent ? [selectedAgent] : [];

  // ADMIN_MEDIA_POPUP_ALWAYS_VISIBLE_FOR_SELECTED_AGENT_V1
  // Admin can see the media options whenever an agent is selected. Client remains creative-agent gated.
  const mediaCapable = mode === "admin"
    ? activeAgents.length > 0
    : activeAgents.some(isCreativeCapableAgent);

  const [open, setOpen] = useState(false);
  const [enabled, setEnabled] = useState(false);
  const [advancedOpen, setAdvancedOpen] = useState(false);

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
  const [ethnicityAppearance, setEthnicityAppearance] = useState("");
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

  const business = businessProfile || {};
  const selectedAgentId = activeAgents.find(isCreativeCapableAgent) || activeAgents[0] || "social_media_manager_content_creator_agent";

  const currentConfig = useMemo(() => ({
    enabled,
    mode,
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
    ethnicity_or_cultural_appearance: ethnicityAppearance,
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
    agent_id: selectedAgentId,
    industry: business.business_niche || business.industry || "",
    target_audience: business.target_audience || "",
    brand_style: business.brand_style || business.notes || "",
    product_or_service_details: business.product_or_service_details || business.services || "",
    speaking_pace: "natural, not rushed",
    lip_sync_accuracy: "high when avatar or talking-head output is requested",
    final_delivery_format: "mp4",
  }), [
    enabled,
    mode,
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
    ethnicityAppearance,
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
    selectedAgentId,
    business.business_niche,
    business.industry,
    business.target_audience,
    business.brand_style,
    business.notes,
    business.product_or_service_details,
    business.services,
  ]);

  // RUN_AGENT_MEDIA_POPUP_CONFIG_BRIDGE_V1
  useEffect(() => {
    onConfigChange?.(currentConfig);
    try {
      window.localStorage.setItem("universal_complete_media_config", JSON.stringify(currentConfig));
      window.dispatchEvent(new CustomEvent("universal-complete-media-config", { detail: currentConfig }));
    } catch {}
  }, [currentConfig, onConfigChange]);

  useEffect(() => {
    const stored = readStoredConfig();
    if (stored?.enabled) {
      setEnabled(Boolean(stored.enabled));
      if (stored.prompt) setPrompt(String(stored.prompt));
      if (stored.output_type) setOutputType(String(stored.output_type));
      if (stored.platform) setPlatform(String(stored.platform));
      if (stored.duration_seconds) setDurationSeconds(String(stored.duration_seconds));
      if (stored.aspect_ratio) setAspectRatio(String(stored.aspect_ratio));
      if (stored.language) setLanguage(String(stored.language));
      if (stored.accent) setAccent(String(stored.accent));
      if (stored.tone) setTone(String(stored.tone));
      if (stored.voice_style) setVoiceStyle(String(stored.voice_style));
      if (stored.call_to_action) setCallToAction(String(stored.call_to_action));
    }
  }, []);

  if (!mediaCapable) {
    return null;
  }

  const selectedAgentLooksCreative = activeAgents.some(isCreativeCapableAgent);
  const statusText = enabled
    ? "Complete media enabled"
    : mode === "admin" && !selectedAgentLooksCreative
    ? "Admin override available"
    : "Optional media output";

  return (
    <div data-run-agent-media-popup="true" data-mode={mode} style={{ marginTop: 12 }}>
      <button
        type="button"
        onClick={() => setOpen(true)}
        style={{
          border: "1px solid rgba(99,102,241,.35)",
          borderRadius: 999,
          padding: "9px 12px",
          background: enabled ? "linear-gradient(135deg,rgba(79,70,229,.24),rgba(6,182,212,.18))" : "rgba(255,255,255,.05)",
          color: mode === "admin" ? "#c4b5fd" : "var(--color-brand, #4f46e5)",
          fontWeight: 950,
          cursor: "pointer",
          display: "inline-flex",
          alignItems: "center",
          gap: 8,
        }}
      >
        🎬 Media options
        <span style={{ opacity: 0.78, fontWeight: 800 }}>· {statusText}</span>
      </button>

      {open ? (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Run Agent media options"
          onClick={() => setOpen(false)}
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
              border: mode === "admin" ? "1px solid rgba(129,140,248,.3)" : "1px solid rgba(226,232,240,.92)",
              background: mode === "admin" ? "#0f1228" : "#ffffff",
              boxShadow: "0 30px 90px rgba(0,0,0,.38)",
              padding: 20,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", gap: 14, alignItems: "flex-start" }}>
              <div>
                <div style={{
                  fontSize: 11,
                  fontWeight: 950,
                  letterSpacing: ".15em",
                  textTransform: "uppercase",
                  color: mode === "admin" ? "#818cf8" : "#4f46e5",
                }}>
                  Run Agent media options
                </div>
                <h3 style={{ margin: "6px 0 0", color: mode === "admin" ? "#fff" : "#0f172a" }}>
                  Complete media output
                </h3>
                <p style={{ margin: "6px 0 0", color: mode === "admin" ? "#94a3b8" : "#64748b", fontSize: 13, lineHeight: 1.5 }}>
                  Configure optional media output here. The actual execution still happens through the main Run Agent button.
                </p>
              </div>

              <button
                type="button"
                onClick={() => setOpen(false)}
                style={{
                  border: "1px solid rgba(148,163,184,.32)",
                  background: mode === "admin" ? "rgba(15,23,42,.9)" : "#fff",
                  color: mode === "admin" ? "#e5e7eb" : "#334155",
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
              <label style={{ display: "flex", alignItems: "center", gap: 9, color: mode === "admin" ? "#e5e7eb" : "#0f172a", fontWeight: 900 }}>
                <input
                  type="checkbox"
                  checked={enabled}
                  onChange={(event) => setEnabled(event.target.checked)}
                />
                Create complete media when Run Agent is clicked
              </label>

              <label style={{ display: "grid", gap: 6, fontSize: 12.5, fontWeight: 850, color: mode === "admin" ? "#cbd5e1" : "#0f172a" }}>
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
                    background: mode === "admin" ? "rgba(15,23,42,.92)" : "#fff",
                    color: mode === "admin" ? "#e5e7eb" : "#0f172a",
                  }}
                />
              </label>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(170px,1fr))", gap: 10 }}>
                <Select label="Output type" value={outputType} onChange={setOutputType} items={outputTypes} mode={mode} />
                <Select label="Platform" value={platform} onChange={setPlatform} items={platforms} mode={mode} />
                <Select label="Duration" value={durationSeconds} onChange={setDurationSeconds} items={durations} mode={mode} suffix="s" />
                <Select label="Aspect ratio" value={aspectRatio} onChange={setAspectRatio} items={aspectRatios} mode={mode} />
                <Field label="Language" value={language} onChange={setLanguage} mode={mode} />
                <Field label="Accent" value={accent} onChange={setAccent} mode={mode} />
              </div>

              <button
                type="button"
                onClick={() => setAdvancedOpen((value) => !value)}
                style={{
                  width: "fit-content",
                  border: "1px solid rgba(99,102,241,.28)",
                  borderRadius: 999,
                  padding: "9px 12px",
                  background: mode === "admin" ? "rgba(79,70,229,.14)" : "#fff",
                  color: mode === "admin" ? "#c4b5fd" : "#4f46e5",
                  fontWeight: 900,
                  cursor: "pointer",
                }}
              >
                {advancedOpen ? "Hide advanced media controls" : "Show advanced media controls"}
              </button>

              {advancedOpen ? (
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))", gap: 10 }}>
                  <Field label="Tone" value={tone} onChange={setTone} mode={mode} />
                  <Field label="Voice style" value={voiceStyle} onChange={setVoiceStyle} mode={mode} />
                  <Field label="Age range" value={ageRange} onChange={setAgeRange} mode={mode} />
                  <Field label="Gender presentation" value={genderPresentation} onChange={setGenderPresentation} mode={mode} />
                  <Field label="Ethnicity / cultural appearance" value={ethnicityAppearance} onChange={setEthnicityAppearance} mode={mode} />
                  <Field label="Ultra-human likeness" value={avatarLikeness} onChange={setAvatarLikeness} mode={mode} />
                  <Field label="Facial features" value={facialFeatures} onChange={setFacialFeatures} mode={mode} />
                  <Field label="Expressions" value={expressions} onChange={setExpressions} mode={mode} />
                  <Field label="Gestures" value={gestures} onChange={setGestures} mode={mode} />
                  <Field label="Wardrobe / styling" value={wardrobe} onChange={setWardrobe} mode={mode} />
                  <Field label="Background / setting" value={backgroundSetting} onChange={setBackgroundSetting} mode={mode} />
                  <Field label="Visual style" value={visualStyle} onChange={setVisualStyle} mode={mode} />
                  <Field label="Camera movement" value={cameraMovement} onChange={setCameraMovement} mode={mode} />
                  <Field label="Music style" value={musicStyle} onChange={setMusicStyle} mode={mode} />
                  <Field label="Sound effects" value={soundEffects} onChange={setSoundEffects} mode={mode} />
                  <Field label="Call-to-action" value={callToAction} onChange={setCallToAction} mode={mode} />
                </div>
              ) : null}

              <div style={{
                borderRadius: 16,
                padding: 12,
                background: mode === "admin" ? "rgba(79,70,229,.12)" : "rgba(79,70,229,.07)",
                color: mode === "admin" ? "#cbd5e1" : "#475569",
                fontSize: 12.5,
                lineHeight: 1.55,
              }}>
                Saved. Close this popup and click the main <strong>Run Agent</strong> button to execute with these media settings.
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function Field({ label, value, onChange, mode }: { label: string; value: string; onChange: (value: string) => void; mode: "client" | "admin" }) {
  return (
    <label style={{ display: "grid", gap: 5, fontSize: 12, fontWeight: 850, color: mode === "admin" ? "#cbd5e1" : "#0f172a" }}>
      {label}
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Optional"
        style={inputStyle(mode)}
      />
    </label>
  );
}

function Select({ label, value, onChange, items, mode, suffix = "" }: { label: string; value: string; onChange: (value: string) => void; items: string[]; mode: "client" | "admin"; suffix?: string }) {
  return (
    <label style={{ display: "grid", gap: 5, fontSize: 12, fontWeight: 850, color: mode === "admin" ? "#cbd5e1" : "#0f172a" }}>
      {label}
      <select value={value} onChange={(event) => onChange(event.target.value)} style={inputStyle(mode)}>
        {items.map((item) => <option key={item} value={item}>{item}{suffix && !String(item).endsWith(suffix) ? suffix : ""}</option>)}
      </select>
    </label>
  );
}

function inputStyle(mode: "client" | "admin"): React.CSSProperties {
  return {
    borderRadius: 12,
    border: "1px solid rgba(148,163,184,.38)",
    padding: "9px 10px",
    fontSize: 12.5,
    background: mode === "admin" ? "rgba(15,23,42,.92)" : "#fff",
    color: mode === "admin" ? "#e5e7eb" : "#0f172a",
  };
}
