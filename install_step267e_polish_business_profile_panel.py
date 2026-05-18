from pathlib import Path
from datetime import datetime
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step267e_polish_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

start = text.find('<section className="rounded-3xl border border-cyan-400/20')
end_marker = '<p className="text-xs font-bold uppercase tracking-[0.3em] text-cyan-300">\n              CLIENT WORKSPACE'
end = text.find(end_marker)

if start == -1:
    raise SystemExit("ERROR: Business Profile panel start marker not found.")

if end == -1:
    raise SystemExit("ERROR: Client Workspace marker not found.")

replacement = '''        <section className="mb-10 rounded-3xl border border-cyan-400/20 bg-cyan-400/[0.04] p-6 shadow-2xl">
          <p className="text-xs font-bold uppercase tracking-[0.3em] text-cyan-300">
            BUSINESS PROFILE INTELLIGENCE
          </p>
          <h2 className="mt-2 text-2xl font-bold text-white">
            Tell your agents about your business
          </h2>
          <p className="mt-2 max-w-4xl text-sm text-slate-300">
            Add details so your AI agents can create more accurate, premium ecommerce outputs.
          </p>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <textarea className="min-h-28 w-full rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-white placeholder:text-slate-500 outline-none focus:border-cyan-300/60" placeholder="Business niche" value={businessProfile.niche} onChange={(event) => setBusinessProfile({ ...businessProfile, niche: event.target.value })} />
            <textarea className="min-h-28 w-full rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-white placeholder:text-slate-500 outline-none focus:border-cyan-300/60" placeholder="Products and services" value={businessProfile.products_services} onChange={(event) => setBusinessProfile({ ...businessProfile, products_services: event.target.value })} />
            <textarea className="min-h-28 w-full rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-white placeholder:text-slate-500 outline-none focus:border-cyan-300/60" placeholder="Target audience" value={businessProfile.target_audience} onChange={(event) => setBusinessProfile({ ...businessProfile, target_audience: event.target.value })} />
            <textarea className="min-h-28 w-full rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-white placeholder:text-slate-500 outline-none focus:border-cyan-300/60" placeholder="Competitors" value={businessProfile.competitors} onChange={(event) => setBusinessProfile({ ...businessProfile, competitors: event.target.value })} />
            <textarea className="min-h-28 w-full rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-white placeholder:text-slate-500 outline-none focus:border-cyan-300/60" placeholder="Offers and promotions" value={businessProfile.offers} onChange={(event) => setBusinessProfile({ ...businessProfile, offers: event.target.value })} />
            <textarea className="min-h-28 w-full rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-white placeholder:text-slate-500 outline-none focus:border-cyan-300/60" placeholder="Brand voice and tone" value={businessProfile.brand_voice} onChange={(event) => setBusinessProfile({ ...businessProfile, brand_voice: event.target.value })} />
            <textarea className="min-h-28 w-full rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-white placeholder:text-slate-500 outline-none focus:border-cyan-300/60" placeholder="Market positioning" value={businessProfile.positioning} onChange={(event) => setBusinessProfile({ ...businessProfile, positioning: event.target.value })} />
            <textarea className="min-h-28 w-full rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-white placeholder:text-slate-500 outline-none focus:border-cyan-300/60" placeholder="Business goals" value={businessProfile.goals} onChange={(event) => setBusinessProfile({ ...businessProfile, goals: event.target.value })} />
          </div>
        </section>

'''

text = text[:start] + replacement + text[end:]

PAGE.write_text(text, encoding="utf-8")

print("STEP_267E_BUSINESS_PROFILE_PANEL_POLISHED")
print(f"Backup: {backup}")
print("STEP_267E_OK")