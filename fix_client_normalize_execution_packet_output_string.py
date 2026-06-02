from pathlib import Path

p = Path("frontend/src/app/client/page.tsx")
text = p.read_text(encoding="utf-8")

old = '''  const output =
    adapter?.output ||
    adapter?.result?.output ||
    data?.output ||
    data?.generated_output ||
    first?.completed_output ||
    first?.deliverable?.content?.body ||
    first?.deliverable?.summary ||
    "";'''

new = '''  const output = customerPortalSafeText(
    adapter?.output ||
      adapter?.result?.output ||
      data?.output ||
      data?.generated_output ||
      first?.completed_output ||
      first?.deliverable?.content?.body ||
      first?.deliverable?.content ||
      first?.deliverable?.output ||
      first?.deliverable?.generated_output ||
      first?.deliverable?.summary ||
      ""
  );'''

if old not in text:
    raise SystemExit("normalizeExecutionPacket output block not found")

text = text.replace(old, new, 1)

p.write_text(text, encoding="utf-8")
print("CLIENT_NORMALIZE_EXECUTION_PACKET_OUTPUT_STRING_FIXED")