from pathlib import Path

p = Path("frontend/src/app/client/page.tsx")
text = p.read_text(encoding="utf-8")

old = '''                  {(liveDeliverable?.tags || ["Deliverable", "Assets", "Execution", "Workflow"]).map((tag: string) => ('''

new = '''                  {(Array.isArray(liveDeliverable?.tags)
                    ? liveDeliverable.tags.filter((tag: any) => typeof tag === "string")
                    : ["Deliverable", "Assets", "Execution", "Workflow"]
                  ).map((tag: string) => ('''

if old not in text:
    raise SystemExit("tags render anchor not found")

text = text.replace(old, new, 1)

p.write_text(text, encoding="utf-8")

print("CLIENT_TAGS_RENDER_HYDRATION_FIXED")