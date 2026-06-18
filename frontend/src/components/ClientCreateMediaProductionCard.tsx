"use client";

import { useState } from "react";

type ClientCreateMediaProductionCardProps = {
  onOpenCreateMedia?: () => void;
};

const humanModes = [
  "No human/avatar",
  "Generate new avatar/person",
  "Use uploaded face/likeness",
  "Use saved brand spokesperson/avatar",
];

const mediaTypes = ["Video", "Audio", "Image", "Full media package"];

export default function ClientCreateMediaProductionCard({
  onOpenCreateMedia,
}: ClientCreateMediaProductionCardProps) {
  const [requestOpen, setRequestOpen] = useState(false);
  const [selectedMediaType, setSelectedMediaType] = useState("Video");
  const [selectedHumanMode, setSelectedHumanMode] = useState("No human/avatar");

  return (
    <section
      data-client-create-media-production-card="true"
      style={{
        margin: "24px 0",
        padding: 24,
        borderRadius: 24,
        border: "1px solid rgba(99, 102, 241, 0.35)",
        background: "linear-gradient(135deg, #071126 0%, #0a1430 54%, #111445 100%)",
        boxShadow: "0 22px 55px rgba(0, 0, 0, 0.26)",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: 18,
          alignItems: "flex-start",
          flexWrap: "wrap",
        }}
      >
        <div style={{ maxWidth: 760 }}>
          <p
            style={{
              margin: "0 0 8px",
              color: "#8ea7ff",
              fontSize: 12,
              fontWeight: 900,
              letterSpacing: "0.12em",
              textTransform: "uppercase",
            }}
          >
            Create Media
          </p>
          <h2
            style={{
              margin: 0,
              color: "#ffffff",
              fontSize: 28,
              lineHeight: 1.15,
              fontWeight: 950,
            }}
          >
            Create media and manage outputs
          </h2>
          <p
            style={{
              margin: "12px 0 0",
              color: "#9fb1d1",
              fontSize: 15,
              lineHeight: 1.7,
            }}
          >
            Build a guided media request without using the old Run Agent workflow.
            Choose the media type, human/avatar mode, and creative direction before
            anything is submitted.
          </p>
        </div>

        <button
          type="button"
          data-client-create-media-open-button="true"
          onClick={() => {
            onOpenCreateMedia?.();
            setRequestOpen((value) => !value);
          }}
          style={{
            border: 0,
            borderRadius: 999,
            padding: "13px 18px",
            background: requestOpen ? "#312e81" : "#6d5dfc",
            color: "#ffffff",
            fontWeight: 950,
            cursor: "pointer",
            boxShadow: "0 12px 28px rgba(109, 93, 252, 0.32)",
          }}
        >
          {requestOpen ? "Close Create Media" : "Open Create Media"}
        </button>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
          gap: 14,
          marginTop: 22,
        }}
      >
        <div
          style={{
            padding: 16,
            borderRadius: 18,
            background: "rgba(8, 18, 42, 0.88)",
            border: "1px solid rgba(99, 102, 241, 0.32)",
          }}
        >
          <h3 style={{ margin: "0 0 10px", color: "#ffffff", fontSize: 15 }}>
            Choose what to create
          </h3>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {mediaTypes.map((type) => (
              <button
                key={type}
                type="button"
                onClick={() => setSelectedMediaType(type)}
                style={{
                  padding: "8px 11px",
                  borderRadius: 999,
                  border: selectedMediaType === type ? "1px solid #a5b4fc" : "1px solid rgba(148, 163, 184, 0.28)",
                  background: selectedMediaType === type ? "rgba(109, 93, 252, 0.28)" : "rgba(15, 23, 42, 0.72)",
                  color: selectedMediaType === type ? "#ffffff" : "#cbd5e1",
                  fontSize: 12,
                  fontWeight: 850,
                  cursor: "pointer",
                }}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        <div
          style={{
            padding: 16,
            borderRadius: 18,
            background: "rgba(8, 18, 42, 0.88)",
            border: "1px solid rgba(99, 102, 241, 0.32)",
          }}
        >
          <h3 style={{ margin: "0 0 10px", color: "#ffffff", fontSize: 15 }}>
            Human mode
          </h3>
          <div style={{ display: "grid", gap: 8 }}>
            {humanModes.map((mode) => (
              <button
                key={mode}
                type="button"
                onClick={() => setSelectedHumanMode(mode)}
                style={{
                  textAlign: "left",
                  padding: "9px 11px",
                  borderRadius: 12,
                  border: selectedHumanMode === mode ? "1px solid #a5b4fc" : "1px solid rgba(148, 163, 184, 0.22)",
                  background: selectedHumanMode === mode ? "rgba(109, 93, 252, 0.28)" : "rgba(15, 23, 42, 0.72)",
                  color: selectedHumanMode === mode ? "#ffffff" : "#cbd5e1",
                  fontSize: 12,
                  fontWeight: 850,
                  cursor: "pointer",
                }}
              >
                {mode}
              </button>
            ))}
          </div>
        </div>

        <div
          style={{
            padding: 16,
            borderRadius: 18,
            background: "rgba(8, 18, 42, 0.88)",
            border: "1px solid rgba(99, 102, 241, 0.32)",
          }}
        >
          <h3 style={{ margin: "0 0 10px", color: "#ffffff", fontSize: 15 }}>
            What happens next
          </h3>
          <p style={{ margin: 0, color: "#9fb1d1", fontSize: 13, lineHeight: 1.6 }}>
            General media uses video, voice, and final composition. Human media
            adds avatar, voice, mouth movement, and performance controls. Technical
            details and diagnostics stay hidden from the client.
          </p>
        </div>
      </div>

      {requestOpen ? (
        <div
          data-client-create-media-request-panel="true"
          style={{
            marginTop: 18,
            padding: 18,
            borderRadius: 18,
            background: "rgba(3, 7, 18, 0.78)",
            border: "1px solid rgba(165, 180, 252, 0.38)",
          }}
        >
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
              gap: 14,
            }}
          >
            <label style={{ display: "grid", gap: 8, color: "#e5e7eb", fontSize: 13, fontWeight: 850 }}>
              Media brief
              <textarea
                placeholder="Describe the video, audio, image, or full media package you want."
                rows={4}
                style={{
                  width: "100%",
                  borderRadius: 14,
                  border: "1px solid rgba(148, 163, 184, 0.32)",
                  background: "#071126",
                  color: "#ffffff",
                  padding: 12,
                  resize: "vertical",
                }}
              />
            </label>

            <label style={{ display: "grid", gap: 8, color: "#e5e7eb", fontSize: 13, fontWeight: 850 }}>
              Creative direction
              <textarea
                placeholder="Style, tone, platform, duration, voice, music, captions, camera, lighting, or brand notes."
                rows={4}
                style={{
                  width: "100%",
                  borderRadius: 14,
                  border: "1px solid rgba(148, 163, 184, 0.32)",
                  background: "#071126",
                  color: "#ffffff",
                  padding: 12,
                  resize: "vertical",
                }}
              />
            </label>
          </div>

          <div
            style={{
              marginTop: 14,
              display: "flex",
              justifyContent: "space-between",
              gap: 12,
              alignItems: "center",
              flexWrap: "wrap",
            }}
          >
            <p style={{ margin: 0, color: "#9fb1d1", fontSize: 13 }}>
              Selected: {selectedMediaType} · {selectedHumanMode}. Submission is intentionally disabled until the governed media job handoff is connected.
            </p>
            <button
              type="button"
              disabled
              style={{
                border: "1px solid rgba(148, 163, 184, 0.35)",
                borderRadius: 999,
                padding: "11px 16px",
                background: "rgba(15, 23, 42, 0.78)",
                color: "#94a3b8",
                fontWeight: 900,
                cursor: "not-allowed",
              }}
            >
              Submit media request soon
            </button>
          </div>
        </div>
      ) : null}

      <div
        style={{
          marginTop: 18,
          padding: 14,
          borderRadius: 16,
          background: "rgba(15, 23, 42, 0.82)",
          border: "1px solid rgba(148, 163, 184, 0.22)",
          color: "#9fb1d1",
          fontSize: 13,
          lineHeight: 1.6,
        }}
      >
        Media job status will show as queued, processing, completed, or failed.
        When an output is ready, preview, open output, request changes, and support
        options should appear here.
      </div>
    </section>
  );
}
