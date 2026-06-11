"use client";

import React, { useEffect, useMemo, useState } from "react";

type UniversalCompleteMediaRunAgentPanelProps = {
  selectedAgent?: string;
  businessProfile?: Record<string, string>;
  onResult?: (deliverable: Record<string, unknown>) => void;
  onConfigChange?: (config: Record<string, unknown>) => void;
};

type UniversalMediaResult = {
  success?: boolean;
  accepted?: boolean;
  polling_required?: boolean;
  job_id?: string;
  status?: string;
  message?: string;
  reason?: string;
  error?: string;
  preview_url?: string;
  signed_preview_url?: string;
  download_url?: string;
  asset_path?: string;
  composition_job_id?: string;
  final_media_type?: string;
  final_duration_seconds?: number;
  playable?: boolean;
  preview_ready?: boolean;
  download_ready?: boolean;
  credential_values_exposed?: boolean;
  customer_safe?: boolean;
  timed_plan?: Array<Record<string, unknown>>;
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

function cleanText(value: unknown, fallback = "") {
  return String(value ?? fallback).trim();
}

function clientSafeAssetUrl(result: UniversalMediaResult | null) {
  if (!result) return "";
  const jobId = cleanText(result.composition_job_id || result.job_id);
  if (!jobId) return "";
  return `/api/universal-complete-media-asset?job_id=${encodeURIComponent(jobId)}`;
}

export default function UniversalCompleteMediaRunAgentPanel({
  selectedAgent,
  businessProfile,
  onResult,
  onConfigChange,
}: UniversalCompleteMediaRunAgentPanelProps) {
  const [enabled, setEnabled] = useState(false);
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [running, setRunning] = useState(false);
  const [pollingJobId, setPollingJobId] = useState("");
  const [message, setMessage] = useState("");
  const [result, setResult] = useState<UniversalMediaResult | null>(null);

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

  const selectedAgentId = selectedAgent || "social_media_manager_content_creator_agent";
  const business = businessProfile || {};
  const previewUrl = result?.preview_url || result?.signed_preview_url || clientSafeAssetUrl(result);

  // UNIVERSAL_COMPLETE_MEDIA_SHARED_STATE_V1
  useEffect(() => {
    onConfigChange?.({
      enabled,
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
    });
  }, [
    enabled,
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
    onConfigChange,
  ]);

  const canGenerate = useMemo(() => enabled && prompt.trim().length >= 3 && !running, [enabled, prompt, running]);

  useEffect(() => {
    if (!pollingJobId) return;

    let cancelled = false;

    const poll = async () => {
      try {
        const response = await fetch(`/api/universal-complete-media-status?job_id=${encodeURIComponent(pollingJobId)}`, {
          method: "GET",
          cache: "no-store",
        });

        const data = await response.json();
        if (cancelled) return;

        setResult(data);
        setMessage(data?.message || data?.reason || data?.status || "Complete media workflow running...");

        if (data?.status === "completed" && data?.playable) {
          setRunning(false);
          setPollingJobId("");
          const assetUrl = clientSafeAssetUrl(data);

          onResult?.({
            title: "Complete media file",
            summary: "Your complete media file is ready for review.",
            output: "Complete synced media file generated from one prompt.",
            generated_output: "Complete synced media file generated from one prompt.",
            content: "Complete synced media file generated from one prompt.",
            preview_url: assetUrl,
            asset_url: assetUrl,
            download_url: assetUrl,
            media_url: assetUrl,
            assets: [
              {
                url: assetUrl,
                title: "Complete media file",
                type: "video",
                source: "universal_complete_media",
              },
            ],
            tags: ["Complete media", "Client safe", "Generated output"],
            created_at: new Date().toISOString(),
          });

          setMessage("Complete media file generated and ready for review.");
          return;
        }

        if (String(data?.status || "").includes("failed") || String(data?.status || "").includes("blocked")) {
          setRunning(false);
          setPollingJobId("");
        }
      } catch {
        if (!cancelled) {
          setMessage("Checking media generation status...");
        }
      }
    };

    poll();
    const timer = window.setInterval(poll, 6000);

    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [pollingJobId, onResult]);

  async function generateCompleteMedia() {
    if (!canGenerate) return;

    setRunning(true);
    setMessage("Starting complete media workflow...");
    setResult(null);

    try {
      const response = await fetch("/api/universal-complete-media", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        cache: "no-store",
        body: JSON.stringify({
          prompt,
          agent_id: selectedAgentId,
          output_type: outputType,
          industry: business.business_niche || business.industry || "",
          target_audience: business.target_audience || "",
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
          brand_style: business.brand_style || business.notes || "",
          product_or_service_details: business.product_or_service_details || business.services || "",
          call_to_action: callToAction,
          music_style: musicStyle,
          sound_effects: soundEffects,
          visual_style: visualStyle,
          camera_movement: cameraMovement,
          speaking_pace: "natural, not rushed",
          lip_sync_accuracy: "high when avatar or talking-head output is requested",
          final_delivery_format: "mp4",
        }),
      });

      const data = await response.json();
      setResult(data);

      if (data?.accepted && data?.job_id) {
        setPollingJobId(data.job_id);
        setMessage("Complete media workflow accepted. Generating visual, natural audio, and final synced file...");
      } else {
        setRunning(false);
        setMessage(data?.reason || data?.message || data?.error || data?.status || "Complete media workflow could not start.");
      }
    } catch (error) {
      setRunning(false);
      setMessage(error instanceof Error ? error.message : "Complete media generation failed.");
    }
  }

  return (
    <div
      data-universal-complete-media-run-agent-panel="true"
      style={{
        marginTop: 14,
        borderRadius: 22,
        border: "1px solid rgba(99,102,241,.22)",
        background: "linear-gradient(135deg,rgba(79,70,229,.08),rgba(6,182,212,.08))",
        padding: 16,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
        <div>
          <div style={{ fontSize: 13, fontWeight: 950, color: "var(--color-brand, #4f46e5)" }}>
            Complete media file
          </div>
          <p style={{ margin: "4px 0 0", fontSize: 12.5, color: "var(--color-muted, #64748b)" }}>
            Prompt once. The system creates visuals, natural audio, synchronises timing, and returns one playable file.
          </p>
        </div>

        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12.5, fontWeight: 850 }}>
          <input
            type="checkbox"
            checked={enabled}
            onChange={(event) => setEnabled(event.target.checked)}
          />
          Create complete media
        </label>
      </div>

      {enabled ? (
        <div style={{ marginTop: 14, display: "grid", gap: 12 }}>
          <label style={{ display: "grid", gap: 6, fontSize: 12.5, fontWeight: 850 }}>
            Media prompt
            <textarea
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              placeholder="Describe the complete media file you want. Include the scene, purpose, presenter/avatar, language, tone, and desired result."
              style={{
                minHeight: 110,
                borderRadius: 16,
                border: "1px solid rgba(148,163,184,.38)",
                padding: 12,
                fontSize: 13,
                background: "#fff",
                color: "#0f172a",
              }}
            />
          </label>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(170px,1fr))", gap: 10 }}>
            <label style={{ display: "grid", gap: 5, fontSize: 12, fontWeight: 850 }}>
              Output type
              <select value={outputType} onChange={(event) => setOutputType(event.target.value)} style={inputStyle}>
                {outputTypes.map((item) => <option key={item}>{item}</option>)}
              </select>
            </label>

            <label style={{ display: "grid", gap: 5, fontSize: 12, fontWeight: 850 }}>
              Platform
              <select value={platform} onChange={(event) => setPlatform(event.target.value)} style={inputStyle}>
                {platforms.map((item) => <option key={item}>{item}</option>)}
              </select>
            </label>

            <label style={{ display: "grid", gap: 5, fontSize: 12, fontWeight: 850 }}>
              Duration
              <select value={durationSeconds} onChange={(event) => setDurationSeconds(event.target.value)} style={inputStyle}>
                {durations.map((item) => <option key={item} value={item}>{item}s</option>)}
              </select>
            </label>

            <label style={{ display: "grid", gap: 5, fontSize: 12, fontWeight: 850 }}>
              Aspect ratio
              <select value={aspectRatio} onChange={(event) => setAspectRatio(event.target.value)} style={inputStyle}>
                {aspectRatios.map((item) => <option key={item}>{item}</option>)}
              </select>
            </label>

            <label style={{ display: "grid", gap: 5, fontSize: 12, fontWeight: 850 }}>
              Language
              <input value={language} onChange={(event) => setLanguage(event.target.value)} style={inputStyle} />
            </label>

            <label style={{ display: "grid", gap: 5, fontSize: 12, fontWeight: 850 }}>
              Accent
              <input value={accent} onChange={(event) => setAccent(event.target.value)} placeholder="Optional" style={inputStyle} />
            </label>
          </div>

          <button
            type="button"
            onClick={() => setAdvancedOpen((value) => !value)}
            style={{
              border: "1px solid rgba(99,102,241,.22)",
              borderRadius: 999,
              padding: "9px 12px",
              background: "#fff",
              color: "#4f46e5",
              fontWeight: 900,
              cursor: "pointer",
              width: "fit-content",
            }}
          >
            {advancedOpen ? "Hide media controls" : "Show media controls"}
          </button>

          {advancedOpen ? (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))", gap: 10 }}>
              <Field label="Tone" value={tone} onChange={setTone} />
              <Field label="Voice style" value={voiceStyle} onChange={setVoiceStyle} />
              <Field label="Age range" value={ageRange} onChange={setAgeRange} />
              <Field label="Gender presentation" value={genderPresentation} onChange={setGenderPresentation} />
              <Field label="Ethnicity / cultural appearance" value={ethnicityAppearance} onChange={setEthnicityAppearance} />
              <Field label="Ultra-human likeness" value={avatarLikeness} onChange={setAvatarLikeness} />
              <Field label="Facial features" value={facialFeatures} onChange={setFacialFeatures} />
              <Field label="Expressions" value={expressions} onChange={setExpressions} />
              <Field label="Gestures" value={gestures} onChange={setGestures} />
              <Field label="Wardrobe / styling" value={wardrobe} onChange={setWardrobe} />
              <Field label="Background / setting" value={backgroundSetting} onChange={setBackgroundSetting} />
              <Field label="Visual style" value={visualStyle} onChange={setVisualStyle} />
              <Field label="Camera movement" value={cameraMovement} onChange={setCameraMovement} />
              <Field label="Music style" value={musicStyle} onChange={setMusicStyle} />
              <Field label="Sound effects" value={soundEffects} onChange={setSoundEffects} />
              <Field label="Call-to-action" value={callToAction} onChange={setCallToAction} />
            </div>
          ) : null}

          <button
            type="button"
            onClick={generateCompleteMedia}
            disabled={!canGenerate}
            style={{
              border: "none",
              borderRadius: 999,
              padding: "12px 16px",
              background: canGenerate ? "linear-gradient(135deg,#4f46e5,#06b6d4)" : "linear-gradient(135deg,#94a3b8,#cbd5e1)",
              color: "#fff",
              fontWeight: 950,
              cursor: canGenerate ? "pointer" : "not-allowed",
              width: "fit-content",
            }}
          >
            {running ? "Generating complete media..." : "Create complete media file"}
          </button>

          {message ? (
            <p style={{ margin: 0, fontSize: 12.5, fontWeight: 850, color: "#475569" }}>
              {message}
            </p>
          ) : null}

          {result?.job_id ? (
            <div style={{ fontSize: 12, color: "#64748b" }}>
              Job: <strong>{result.job_id}</strong> · Status: <strong>{result.status || "queued"}</strong>
            </div>
          ) : null}

          {previewUrl && result?.playable ? (
            <video
              src={previewUrl}
              controls
              playsInline
              style={{
                width: "100%",
                maxHeight: 420,
                borderRadius: 18,
                border: "1px solid rgba(148,163,184,.28)",
                background: "#020617",
              }}
            />
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

function Field({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label style={{ display: "grid", gap: 5, fontSize: 12, fontWeight: 850 }}>
      {label}
      <input value={value} onChange={(event) => onChange(event.target.value)} placeholder="Optional" style={inputStyle} />
    </label>
  );
}

const inputStyle: React.CSSProperties = {
  borderRadius: 12,
  border: "1px solid rgba(148,163,184,.38)",
  padding: "9px 10px",
  fontSize: 12.5,
  background: "#fff",
  color: "#0f172a",
};
