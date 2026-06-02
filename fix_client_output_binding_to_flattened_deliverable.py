from pathlib import Path

p = Path("frontend/src/app/client/page.tsx")
text = p.read_text(encoding="utf-8")

old = '''  const visibleClientOutcomeText =
    mediaPackSummaryText ||
    liveDeliverableAny?.output ||
    liveDeliverableAny?.generated_output ||
    liveDeliverableAny?.provider_output ||
    liveDeliverableAny?.content ||
    liveDeliverableAny?.summary ||
    liveDeliverableAny?.message ||
    "";'''

new = '''  const visibleClientOutcomeText =
    customerPortalSafeText(liveDeliverableAny?.output) ||
    customerPortalSafeText(liveDeliverableAny?.generated_output) ||
    customerPortalSafeText(liveDeliverableAny?.content) ||
    customerPortalSafeText(liveDeliverableAny?.provider_output) ||
    mediaPackSummaryText ||
    customerPortalSafeText(liveDeliverableAny?.summary) ||
    customerPortalSafeText(liveDeliverableAny?.message) ||
    "";'''

if old not in text:
    raise SystemExit("visibleClientOutcomeText block not found")

text = text.replace(old, new, 1)

text = text.replace(
    '''{visibleClientOutcomeText || "No generated outcome is ready yet. Run an agent to create a client deliverable."}''',
    '''{customerPortalSafeText(
                          visibleClientOutcomeText,
                          "No generated outcome is ready yet. Run an agent to create a client deliverable."
                        )}'''
)

text = text.replace(
    '''{liveDeliverable?.summary ||
                    "Client-specific deliverable generated from the latest execution, business profile, selected agents, and review requirements."}''',
    '''{customerPortalSafeText(
                    liveDeliverable?.summary,
                    "Client-specific deliverable generated from the latest execution, business profile, selected agents, and review requirements."
                  )}'''
)

text = text.replace(
    '''const shareText = `${liveDeliverable?.title || "Client deliverable"} ΓÇö ${liveDeliverable?.summary || "Ready for review."}`;''',
    '''const shareText = `${liveDeliverable?.title || "Client deliverable"} - ${customerPortalSafeText(liveDeliverable?.summary, "Ready for review.")}`;'''
)

p.write_text(text, encoding="utf-8")
print("CLIENT_OUTPUT_BOUND_TO_FLATTENED_DELIVERABLE")