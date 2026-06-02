from pathlib import Path

p = Path("frontend/src/app/client/page.tsx")
text = p.read_text(encoding="utf-8")

# Strengthen customerPortalSafeText so objects never get rendered directly.
old = '''function customerPortalSafeText(value: unknown, fallback = "") {
  if (typeof value === "string") return value;
  if (value === null || value === undefined) return fallback;
  return String(value);
}
'''

new = '''function customerPortalSafeText(value: unknown, fallback = "") {
  if (typeof value === "string") return value;
  if (value === null || value === undefined) return fallback;

  if (typeof value === "object") {
    const anyValue = value as any;

    const preferred =
      anyValue?.provider_execution?.generated_content ||
      anyValue?.provider_connector?.generated_content ||
      anyValue?.generated_content ||
      anyValue?.content ||
      anyValue?.summary ||
      anyValue?.message ||
      anyValue?.safe_client_message ||
      "";

    if (typeof preferred === "string" && preferred.trim()) {
      return preferred;
    }

    try {
      return JSON.stringify(value, null, 2);
    } catch {
      return fallback;
    }
  }

  return String(value);
}
'''

if old not in text:
    raise SystemExit("customerPortalSafeText anchor not found")

text = text.replace(old, new, 1)

# Make visible outcome text use safe text extraction.
start = text.find("  const visibleClientOutcomeText =")
if start == -1:
    raise SystemExit("visibleClientOutcomeText start not found")

end = text.find("\n\nconst primaryAssetUrl", start)
if end == -1:
    raise SystemExit("visibleClientOutcomeText end not found")

replacement = '''  const visibleClientOutcomeText =
    mediaPackSummaryText ||
    customerPortalSafeText(liveDeliverableAny?.output) ||
    customerPortalSafeText(liveDeliverableAny?.generated_output) ||
    customerPortalSafeText(liveDeliverableAny?.provider_output) ||
    customerPortalSafeText(liveDeliverableAny?.content) ||
    customerPortalSafeText(liveDeliverableAny?.summary) ||
    customerPortalSafeText(liveDeliverableAny?.message) ||
    "";
'''

text = text[:start] + replacement + text[end:]

# Prevent summary object rendering in latest deliverable panel.
text = text.replace(
    '''{liveDeliverable?.summary ||
                    "Client-specific deliverable generated from the latest execution, business profile, selected agents, and review requirements."}''',
    '''{customerPortalSafeText(
                    liveDeliverable?.summary,
                    "Client-specific deliverable generated from the latest execution, business profile, selected agents, and review requirements."
                  )}'''
)

# Prevent copy/share text from stringifying as [object Object].
text = text.replace(
    '''const shareText = `${liveDeliverable?.title || "Client deliverable"} ΓÇö ${liveDeliverable?.summary || "Ready for review."}`;''',
    '''const shareText = `${liveDeliverable?.title || "Client deliverable"} - ${customerPortalSafeText(liveDeliverable?.summary, "Ready for review.")}`;'''
)

p.write_text(text, encoding="utf-8")
print("CLIENT_OBJECT_RENDER_CRASH_FIXED")