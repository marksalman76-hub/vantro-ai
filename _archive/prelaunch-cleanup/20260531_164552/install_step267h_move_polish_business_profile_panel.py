from pathlib import Path
from datetime import datetime
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step267h_move_polish_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

panel = '''        <section className="rounded-3xl border border-cyan-400/20 bg-slate-900/70 p-6 shadow-2xl">
          <div className="mb-5">
            <p className="text-xs font-bold uppercase tracking-[0.28em] text-cyan-300">
              BUSINESS PROFILE INTELLIGENCE
            </p>
            <h2 className="mt-2 text-2xl font-bold text-white">
              Business context for smarter agent outputs
            </h2>
            <p className="mt-2 max-w-4xl text-sm leading-6 text-slate-300">
              Add your store context once so every agent can produce more accurate, premium ecommerce work.
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <textarea className="min-h-20 w-full rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-sm text-white placeholder:text-slate-500 outline-none focus:border-cyan-300/70" placeholder="Business niche" value={businessProfile.niche} onChange={(event) => setBusinessProfile({ ...businessProfile, niche: event.target.value })} />
            <textarea className="min-h-20 w-full rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-sm text-white placeholder:text-slate-500 outline-none focus:border-cyan-300/70" placeholder="Products and services" value={businessProfile.products_services} onChange={(event) => setBusinessProfile({ ...businessProfile, products_services: event.target.value })} />
            <textarea className="min-h-20 w-full rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-sm text-white placeholder:text-slate-500 outline-none focus:border-cyan-300/70" placeholder="Target audience" value={businessProfile.target_audience} onChange={(event) => setBusinessProfile({ ...businessProfile, target_audience: event.target.value })} />
            <textarea className="min-h-20 w-full rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-sm text-white placeholder:text-slate-500 outline-none focus:border-cyan-300/70" placeholder="Competitors" value={businessProfile.competitors} onChange={(event) => setBusinessProfile({ ...businessProfile, competitors: event.target.value })} />
            <textarea className="min-h-20 w-full rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-sm text-white placeholder:text-slate-500 outline-none focus:border-cyan-300/70" placeholder="Offers and promotions" value={businessProfile.offers} onChange={(event) => setBusinessProfile({ ...businessProfile, offers: event.target.value })} />
            <textarea className="min-h-20 w-full rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-sm text-white placeholder:text-slate-500 outline-none focus:border-cyan-300/70" placeholder="Brand voice and tone" value={businessProfile.brand_voice} onChange={(event) => setBusinessProfile({ ...businessProfile, brand_voice: event.target.value })} />
            <textarea className="min-h-20 w-full rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-sm text-white placeholder:text-slate-500 outline-none focus:border-cyan-300/70" placeholder="Market positioning" value={businessProfile.positioning} onChange={(event) => setBusinessProfile({ ...businessProfile, positioning: event.target.value })} />
            <textarea className="min-h-20 w-full rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-sm text-white placeholder:text-slate-500 outline-none focus:border-cyan-300/70" placeholder="Business goals" value={businessProfile.goals} onChange={(event) => setBusinessProfile({ ...businessProfile, goals: event.target.value })} />
          </div>
        </section>

'''

# Remove any existing business profile panel/block before reinserting cleanly
if "BUSINESS PROFILE INTELLIGENCE" in text:
    marker = text.find("BUSINESS PROFILE INTELLIGENCE")
    old_section_start = text.rfind("<section", 0, marker)
    next_workspace = text.find("CLIENT WORKSPACE", marker)
    next_run = text.find("Run AI Agent", marker)

    if old_section_start != -1:
        if next_workspace != -1:
            old_section_end = text.rfind("<p", 0, next_workspace)
        elif next_run != -1:
            old_section_end = text.rfind("<section", 0, next_run)
        else:
            old_section_end = -1

        if old_section_end != -1 and old_section_end > old_section_start:
            text = text[:old_section_start] + text[old_section_end:]

# Remove leftover style block from Step 267G if present
text = re.sub(
    r'\s*<style jsx>\{`\s*\.business-profile-field[\s\S]*?\s*`\}</style>\s*',
    "\n",
    text,
    count=1,
)

# Insert before Run AI Agent section
run_pos = text.find("Run AI Agent")
if run_pos == -1:
    raise SystemExit("ERROR: Could not find Run AI Agent marker.")

run_section_start = text.rfind("<section", 0, run_pos)
if run_section_start == -1:
    raise SystemExit("ERROR: Could not locate Run AI Agent section.")

text = text[:run_section_start] + panel + text[run_section_start:]

PAGE.write_text(text, encoding="utf-8")

print("STEP_267H_BUSINESS_PROFILE_MOVED_AND_POLISHED")
print(f"Backup: {backup}")
print("STEP_267H_OK")