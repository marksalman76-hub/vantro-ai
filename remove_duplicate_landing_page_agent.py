from pathlib import Path

p = Path("frontend/src/app/signup/page.tsx")
s = p.read_text(encoding="utf-8")

backup = Path("backups/signup_before_remove_duplicate_landing_page_agent.tsx")
backup.parent.mkdir(exist_ok=True)
backup.write_text(s, encoding="utf-8")

target = '  ["landing_page_agent", "Landing Page Agent", "Content & Creative", "Landing page structure, offer sections, conversion copy, page flow, and CTA optimisation."],\n'

if target not in s:
    raise SystemExit("LANDING_PAGE_AGENT_TARGET_NOT_FOUND")

s = s.replace(target, "")

p.write_text(s, encoding="utf-8")
print("DUPLICATE_LANDING_PAGE_AGENT_REMOVED")
print("Backup:", backup)