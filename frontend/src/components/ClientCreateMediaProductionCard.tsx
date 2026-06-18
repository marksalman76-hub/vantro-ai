"use client";

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
  return (
    <section
      data-client-create-media-production-card="true"
      style={{
        margin: "24px 0",
        padding: 24,
        borderRadius: 24,
        border: "1px solid #dbe4f0",
        background: "linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)",
        boxShadow: "0 18px 45px rgba(15, 23, 42, 0.08)",
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
        <div style={{ maxWidth: 720 }}>
          <p
            style={{
              margin: "0 0 8px",
              color: "#64748b",
              fontSize: 12,
              fontWeight: 800,
              letterSpacing: "0.12em",
              textTransform: "uppercase",
            }}
          >
            Create Media
          </p>
          <h2
            style={{
              margin: 0,
              color: "#0f172a",
              fontSize: 28,
              lineHeight: 1.15,
              fontWeight: 900,
            }}
          >
            Create media and manage outputs
          </h2>
          <p
            style={{
              margin: "12px 0 0",
              color: "#475569",
              fontSize: 15,
              lineHeight: 1.7,
            }}
          >
            Build a guided media request without using the old Run Agent workflow.
            Choose the type of media, select whether a human/avatar is needed,
            add creative direction, then submit only when you are ready.
          </p>
        </div>

        <button
          type="button"
          onClick={onOpenCreateMedia}
          style={{
            border: 0,
            borderRadius: 999,
            padding: "13px 18px",
            background: "#4f46e5",
            color: "#ffffff",
            fontWeight: 900,
            cursor: "pointer",
            boxShadow: "0 12px 28px rgba(79, 70, 229, 0.28)",
          }}
        >
          Open Create Media
        </button>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: 14,
          marginTop: 22,
        }}
      >
        <div
          style={{
            padding: 16,
            borderRadius: 18,
            background: "#ffffff",
            border: "1px solid #e2e8f0",
          }}
        >
          <h3 style={{ margin: "0 0 10px", color: "#0f172a", fontSize: 15 }}>
            Choose what to create
          </h3>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {mediaTypes.map((type) => (
              <span
                key={type}
                style={{
                  padding: "7px 10px",
                  borderRadius: 999,
                  background: "#eef2ff",
                  color: "#3730a3",
                  fontSize: 12,
                  fontWeight: 800,
                }}
              >
                {type}
              </span>
            ))}
          </div>
        </div>

        <div
          style={{
            padding: 16,
            borderRadius: 18,
            background: "#ffffff",
            border: "1px solid #e2e8f0",
          }}
        >
          <h3 style={{ margin: "0 0 10px", color: "#0f172a", fontSize: 15 }}>
            Human mode
          </h3>
          <div style={{ display: "grid", gap: 8 }}>
            {humanModes.map((mode) => (
              <div
                key={mode}
                style={{
                  padding: "8px 10px",
                  borderRadius: 12,
                  background: "#f8fafc",
                  color: "#334155",
                  fontSize: 12,
                  fontWeight: 750,
                }}
              >
                {mode}
              </div>
            ))}
          </div>
        </div>

        <div
          style={{
            padding: 16,
            borderRadius: 18,
            background: "#ffffff",
            border: "1px solid #e2e8f0",
          }}
        >
          <h3 style={{ margin: "0 0 10px", color: "#0f172a", fontSize: 15 }}>
            What happens next
          </h3>
          <p style={{ margin: 0, color: "#475569", fontSize: 13, lineHeight: 1.6 }}>
            General media uses video, voice, and final composition. Human media
            uses avatar, voice, mouth movement, and final composition. Provider names
            and technical diagnostics stay hidden from the client.
          </p>
        </div>
      </div>

      <div
        style={{
          marginTop: 18,
          padding: 14,
          borderRadius: 16,
          background: "#f8fafc",
          color: "#475569",
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
