from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "frontend" / "src" / "app" / "admin" / "live-execution" / "page.tsx"

BACKUP = ROOT / "backups" / f"visual_deliverable_preview_cards_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "page.tsx")

s = TARGET.read_text(encoding="utf-8")

helper = r'''
function buildVisualDeliverableCards(output: string, agentLabel: string) {
  const text = String(output || "").trim();
  if (!text) return [];

  const lower = `${agentLabel} ${text}`.toLowerCase();

  if (lower.includes("paid ads") || lower.includes("meta ads") || lower.includes("google search") || lower.includes("ad variation")) {
    return [
      { title: "Campaign Board", detail: "Paid ad concepts, hooks, audiences and CTA variants generated." },
      { title: "Meta Ad Preview", detail: "Primary text, headline and CTA structure ready for review." },
      { title: "Google Search Pack", detail: "Search headlines and descriptions prepared for campaign build." },
      { title: "Short-Form Scripts", detail: "TikTok/Reels scripts and hook structure prepared." },
    ];
  }

  if (lower.includes("ugc") || lower.includes("video concept") || lower.includes("shot-by-shot") || lower.includes("creator")) {
    return [
      { title: "UGC Storyboard", detail: "Shot-by-shot video concepts generated for creator production." },
      { title: "Creator Direction", detail: "Casting, wardrobe, lighting and camera guidance prepared." },
      { title: "Retention Map", detail: "Hooks and pacing beats prepared for short-form performance." },
      { title: "Paid Social Variants", detail: "Ad-ready UGC concepts prepared for campaign testing." },
    ];
  }

  if (lower.includes("seo") || lower.includes("meta description") || lower.includes("keyword")) {
    return [
      { title: "SEO Brief", detail: "Title, meta description and keyword structure generated." },
      { title: "Search Intent Map", detail: "Primary and secondary optimisation angles prepared." },
      { title: "Content Blocks", detail: "Page optimisation and content guidance ready for review." },
    ];
  }

  if (lower.includes("email") || lower.includes("subject")) {
    return [
      { title: "Email Draft", detail: "Subject line and email body generated." },
      { title: "Reply Preview", detail: "Client-safe message ready for review or send workflow." },
    ];
  }

  return [
    { title: "Deliverable Preview", detail: "Generated output is ready for review in the live output panel." },
    { title: "Execution Packet", detail: "Autonomous run completed and saved to history." },
  ];
}
'''

if "function buildVisualDeliverableCards" not in s:
    anchor = "function normalizeExecutionPacket"
    s = s.replace(anchor, helper + "\n\n" + anchor)

# Add derived cards near normalizedResult if available.
if "const visualDeliverableCards = buildVisualDeliverableCards" not in s:
    s = s.replace(
        "const normalizedResult = normalizeExecutionPacket(result);",
        'const normalizedResult = normalizeExecutionPacket(result);\n  const visualDeliverableCards = buildVisualDeliverableCards(normalizedResult?.output || "", selectedAgents.length > 1 ? `${selectedAgents.length} agents` : agentName(agent));'
    )

old = '''<div style={{ fontSize: 34, marginBottom: 10 }}>🖼️</div>
                        <div style={{ fontWeight: 950, color: "#fff" }}>Media assets will appear here</div>
                        <div style={{ color: "#c7d2fe", lineHeight: 1.35 }}>
                          Generated images, video, uploaded files, and media previews will appear here when an execution includes assets.
                        </div>'''

new = '''{visualDeliverableCards.length > 0 ? (
                          <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: 12, width: "100%", textAlign: "left" }}>
                            {visualDeliverableCards.map((card, idx) => (
                              <div key={`${card.title}-${idx}`} style={{ border: "1px solid rgba(125,211,252,.28)", background: "rgba(14,165,233,.08)", borderRadius: 18, padding: 14 }}>
                                <div style={{ fontSize: 12, color: "#67e8f9", fontWeight: 950, marginBottom: 6 }}>PREVIEW {idx + 1}</div>
                                <div style={{ fontWeight: 950, color: "#fff", marginBottom: 6 }}>{card.title}</div>
                                <div style={{ color: "#c7d2fe", fontSize: 13, lineHeight: 1.35 }}>{card.detail}</div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <>
                            <div style={{ fontSize: 34, marginBottom: 10 }}>🖼️</div>
                            <div style={{ fontWeight: 950, color: "#fff" }}>Media assets will appear here</div>
                            <div style={{ color: "#c7d2fe", lineHeight: 1.35 }}>
                              Generated images, video, uploaded files, and media previews will appear here when an execution includes assets.
                            </div>
                          </>
                        )}'''

if old in s:
    s = s.replace(old, new)
else:
    print("WARNING: media placeholder block not found; helper/state added only.")

TARGET.write_text(s, encoding="utf-8")

print("VISUAL_DELIVERABLE_PREVIEW_CARDS_ADDED")
print("Backup:", BACKUP)
print("Updated:", TARGET)