from pathlib import Path
import re
import json
from datetime import datetime
import shutil

ROOT = Path(__file__).resolve().parent
COMPONENT = ROOT / "frontend" / "src" / "components" / "ClientCreateMediaProductionCard.tsx"
VERIFY = ROOT / "verify_isolated_client_media_card.py"

backup_dir = ROOT / "backups" / f"client_media_card_click_bridge_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(COMPONENT, backup_dir / "ClientCreateMediaProductionCard.tsx")

component = r'''
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

function findExistingCreateMediaButton(currentButton: HTMLButtonElement | null) {
  const buttons = Array.from(document.querySelectorAll("button")) as HTMLButtonElement[];

  const directSelectorButton = document.querySelector(
    '[data-open-create-media], [data-create-media-open], button[aria-label="Create Media"]',
  ) as HTMLButtonElement | null;

  if (directSelectorButton && directSelectorButton !== currentButton) {
    return directSelectorButton;
  }

  const preferredTextMatches = [
    "create media",
    "create complete media",
    "complete media",
    "direct media",
    "open media",
    "generate media",
  ];

  return (
    buttons.find((button) => {
      if (button === currentButton) {
        return false;
      }

      const label = `${button.textContent || ""} ${button.getAttribute("aria-label") || ""}`
        .trim()
        .toLowerCase();

      if (!label) {
        return false;
      }

      return preferredTextMatches.some((match) => label.includes(match));
    }) || null
  );
}

export default function ClientCreateMediaProductionCard({
  onOpenCreateMedia,
}: ClientCreateMediaProductionCardProps) {
  const handleOpenCreateMedia = (event: React.MouseEvent<HTMLButtonElement>) => {
    onOpenCreateMedia?.();

    window.setTimeout(() => {
      const existingButton = findExistingCreateMediaButton(event.currentTarget);
      if (existingButton) {
        existingButton.click();
        return;
      }

      const mediaSection = document.querySelector(
        "[data-complete-media-popup], [data-media-workflow], [data-client-media-assets], #create-media, #media",
      ) as HTMLElement | null;

      mediaSection?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 0);
  };

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
          data-client-create-media-open-button="true"
          onClick={handleOpenCreateMedia}
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
            uses avatar, voice, mouth movement, and final composition. Technical
            details and diagnostics stay hidden from the client.
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
'''.lstrip()

COMPONENT.write_text(component, encoding="utf-8", newline="\n")

verify_text = VERIFY.read_text(encoding="utf-8", errors="ignore")
if "open_button_bridge_present" not in verify_text:
    verify_text = verify_text.replace(
        '"component_mounted_in_client_page": "<ClientCreateMediaProductionCard" in client_text,',
        '"component_mounted_in_client_page": "<ClientCreateMediaProductionCard" in client_text,\n'
        '    "open_button_bridge_present": "data-client-create-media-open-button" in component_text and "findExistingCreateMediaButton" in component_text,',
    )
    verify_text = verify_text.replace(
        'and proof["use_client_first_line_component"]\n',
        'and proof["use_client_first_line_component"]\n'
        '    and proof["open_button_bridge_present"]\n',
    )

VERIFY.write_text(verify_text, encoding="utf-8", newline="\n")

print(json.dumps({
    "click_bridge_fixed": True,
    "component": str(COMPONENT),
    "verifier": str(VERIFY),
    "backup": str(backup_dir),
    "provider_calls": False,
    "media_generation": False,
    "billing_mutation": False,
    "credit_mutation": False,
    "stripe": False,
}, indent=2))