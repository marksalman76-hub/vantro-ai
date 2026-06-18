from pathlib import Path
import re
import json
from datetime import datetime
import shutil

ROOT = Path(__file__).resolve().parent
CLIENT_PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
COMPONENT = ROOT / "frontend" / "src" / "components" / "ClientCreateMediaProductionCard.tsx"
VERIFY = ROOT / "verify_isolated_client_media_card.py"

backup_dir = ROOT / "backups" / f"isolated_client_media_card_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(CLIENT_PAGE, backup_dir / "client_page.tsx")

COMPONENT.parent.mkdir(parents=True, exist_ok=True)

COMPONENT.write_text(r'''
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
            uses avatar, voice, lip-sync, and final composition. Provider names
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
'''.lstrip(), encoding="utf-8")

text = CLIENT_PAGE.read_text(encoding="utf-8-sig", errors="ignore")
text = text.replace("\ufeff", "")

# Keep existing use client directive exactly once.
text = re.sub(r'(?m)^\s*[\'"]use client[\'"];\s*\r?\n?', "", text)
text = '"use client";\n\n' + text.strip() + "\n"

import_line = 'import ClientCreateMediaProductionCard from "../../components/ClientCreateMediaProductionCard";'
if import_line not in text:
    lines = text.splitlines()
    insert_at = 1
    while insert_at < len(lines) and (lines[insert_at].startswith("import ") or lines[insert_at].strip() == ""):
        insert_at += 1
    lines.insert(insert_at, import_line)
    text = "\n".join(lines) + "\n"

card = '''
      <ClientCreateMediaProductionCard
        onOpenCreateMedia={() => {
          const button = document.querySelector('[data-open-create-media], [data-create-media-open], button[aria-label="Create Media"]') as HTMLButtonElement | null;
          button?.click();
        }}
      />
'''

if "data-client-create-media-production-card" not in text and "<ClientCreateMediaProductionCard" not in text:
    # Insert immediately after the first <main...> opening tag if available.
    match = re.search(r'(<main[^>]*>)', text)
    if match:
        text = text[: match.end()] + "\n" + card + text[match.end():]
    else:
        # Safe fallback: put the card after the first return fragment/opening div.
        text = text.replace("return (", "return (\n" + card, 1)

text = "\n".join(line.rstrip() for line in text.splitlines()).strip() + "\n"
CLIENT_PAGE.write_text(text, encoding="utf-8", newline="\n")

VERIFY.write_text(r'''
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
client_page = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
component = ROOT / "frontend" / "src" / "components" / "ClientCreateMediaProductionCard.tsx"

client_text = client_page.read_text(encoding="utf-8", errors="ignore")
component_text = component.read_text(encoding="utf-8", errors="ignore") if component.exists() else ""

required_component_phrases = [
    "Create Media",
    "Create media and manage outputs",
    "No human/avatar",
    "Generate new avatar/person",
    "Use uploaded face/likeness",
    "Use saved brand spokesperson/avatar",
    "queued, processing, completed, or failed",
]

proof = {
    "isolated_client_media_card_attempted": True,
    "isolated_client_media_card_passed": True,
    "component_exists": component.exists(),
    "component_imported_by_client_page": "ClientCreateMediaProductionCard" in client_text,
    "component_mounted_in_client_page": "<ClientCreateMediaProductionCard" in client_text,
    "use_client_first_line_client_page": client_text.splitlines()[0].strip() == '"use client";',
    "use_client_first_line_component": component_text.splitlines()[0].strip() == '"use client";' if component_text else False,
    "required_component_phrases_present": {phrase: phrase in component_text for phrase in required_component_phrases},
    "provider_names_hidden_from_component": all(
        name not in component_text.lower()
        for name in ["kling", "runway", "heygen", "sync", "elevenlabs", "ffmpeg"]
    ),
    "provider_call_attempted": False,
    "media_generation_attempted": False,
    "billing_mutation_attempted": False,
    "credit_mutation_attempted": False,
    "stripe_live_charge_attempted": False,
    "aws21_or_later_work_attempted": False,
    "public_cutover_enabled": False,
    "next_operator_action": "review_client_create_media_card_in_browser",
}

proof["isolated_client_media_card_passed"] = (
    proof["component_exists"]
    and proof["component_imported_by_client_page"]
    and proof["component_mounted_in_client_page"]
    and proof["use_client_first_line_client_page"]
    and proof["use_client_first_line_component"]
    and all(proof["required_component_phrases_present"].values())
    and proof["provider_names_hidden_from_component"]
)

print("ISOLATED_CLIENT_MEDIA_CARD_PROOF:")
print(json.dumps(proof, indent=2, sort_keys=True))

if not proof["isolated_client_media_card_passed"]:
    raise SystemExit("ISOLATED_CLIENT_MEDIA_CARD_FAILED")

print("ISOLATED_CLIENT_MEDIA_CARD_PASSED")
'''.lstrip(), encoding="utf-8")

print(json.dumps({
    "component": str(COMPONENT),
    "client_page": str(CLIENT_PAGE),
    "backup": str(backup_dir),
    "verifier": str(VERIFY),
    "provider_calls": False,
    "media_generation": False,
    "billing_mutation": False,
    "credit_mutation": False,
    "stripe": False,
}, indent=2))