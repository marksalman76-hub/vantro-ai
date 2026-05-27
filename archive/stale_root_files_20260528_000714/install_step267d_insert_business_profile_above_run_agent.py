from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step267d_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

panel = '''
        <section className="rounded-3xl border border-cyan-400/20 bg-cyan-400/[0.04] p-6 shadow-2xl">
          <p className="text-xs font-bold uppercase tracking-[0.3em] text-cyan-300">
            BUSINESS PROFILE INTELLIGENCE
          </p>
          <h2 className="mt-2 text-2xl font-bold text-white">
            Tell your agents about your business
          </h2>
          <p className="mt-2 text-sm text-slate-300">
            Add details so your AI agents can create more accurate, premium ecommerce outputs.
          </p>

          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <textarea className="min-h-24 rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-white" placeholder="Business niche" value={businessProfile.niche} onChange={(event) => setBusinessProfile({ ...businessProfile, niche: event.target.value })} />
            <textarea className="min-h-24 rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-white" placeholder="Products and services" value={businessProfile.products_services} onChange={(event) => setBusinessProfile({ ...businessProfile, products_services: event.target.value })} />
            <textarea className="min-h-24 rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-white" placeholder="Target audience" value={businessProfile.target_audience} onChange={(event) => setBusinessProfile({ ...businessProfile, target_audience: event.target.value })} />
            <textarea className="min-h-24 rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-white" placeholder="Competitors" value={businessProfile.competitors} onChange={(event) => setBusinessProfile({ ...businessProfile, competitors: event.target.value })} />
            <textarea className="min-h-24 rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-white" placeholder="Offers and promotions" value={businessProfile.offers} onChange={(event) => setBusinessProfile({ ...businessProfile, offers: event.target.value })} />
            <textarea className="min-h-24 rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-white" placeholder="Brand voice and tone" value={businessProfile.brand_voice} onChange={(event) => setBusinessProfile({ ...businessProfile, brand_voice: event.target.value })} />
            <textarea className="min-h-24 rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-white" placeholder="Market positioning" value={businessProfile.positioning} onChange={(event) => setBusinessProfile({ ...businessProfile, positioning: event.target.value })} />
            <textarea className="min-h-24 rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-white" placeholder="Business goals" value={businessProfile.goals} onChange={(event) => setBusinessProfile({ ...businessProfile, goals: event.target.value })} />
          </div>
        </section>

'''

if "BUSINESS PROFILE INTELLIGENCE" not in text:
    run_agent_pos = text.find("Run AI Agent")
    if run_agent_pos == -1:
        raise SystemExit("ERROR: Could not find Run AI Agent marker.")

    section_pos = text.rfind("<section", 0, run_agent_pos)
    if section_pos == -1:
        raise SystemExit("ERROR: Could not find section before Run AI Agent.")

    text = text[:section_pos] + panel + text[section_pos:]

PAGE.write_text(text, encoding="utf-8")

print("STEP_267D_BUSINESS_PROFILE_PANEL_INSERTED")
print(f"Backup: {backup}")
print("STEP_267D_OK")