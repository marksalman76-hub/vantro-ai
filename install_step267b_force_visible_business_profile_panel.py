from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step267b_visible_panel_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

panel = r'''
        <section className="rounded-3xl border border-white/10 bg-white/[0.04] p-6 shadow-2xl">
          <div className="mb-5">
            <p className="text-xs font-bold uppercase tracking-[0.3em] text-cyan-300">
              BUSINESS PROFILE INTELLIGENCE
            </p>
            <h2 className="mt-2 text-2xl font-bold text-white">
              Tell your agents about your business
            </h2>
            <p className="mt-2 text-sm text-slate-300">
              Add your niche, products, audience, competitors, offers, brand voice, positioning, and goals so your AI agents can produce more accurate, premium ecommerce outputs.
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <textarea
              className="min-h-28 rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-white outline-none"
              placeholder="Business niche"
              value={businessProfile.niche}
              onChange={(event) => setBusinessProfile({ ...businessProfile, niche: event.target.value })}
            />

            <textarea
              className="min-h-28 rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-white outline-none"
              placeholder="Products and services"
              value={businessProfile.products_services}
              onChange={(event) => setBusinessProfile({ ...businessProfile, products_services: event.target.value })}
            />

            <textarea
              className="min-h-28 rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-white outline-none"
              placeholder="Target audience"
              value={businessProfile.target_audience}
              onChange={(event) => setBusinessProfile({ ...businessProfile, target_audience: event.target.value })}
            />

            <textarea
              className="min-h-28 rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-white outline-none"
              placeholder="Competitors"
              value={businessProfile.competitors}
              onChange={(event) => setBusinessProfile({ ...businessProfile, competitors: event.target.value })}
            />

            <textarea
              className="min-h-28 rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-white outline-none"
              placeholder="Offers and promotions"
              value={businessProfile.offers}
              onChange={(event) => setBusinessProfile({ ...businessProfile, offers: event.target.value })}
            />

            <textarea
              className="min-h-28 rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-white outline-none"
              placeholder="Brand voice and tone"
              value={businessProfile.brand_voice}
              onChange={(event) => setBusinessProfile({ ...businessProfile, brand_voice: event.target.value })}
            />

            <textarea
              className="min-h-28 rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-white outline-none"
              placeholder="Market positioning"
              value={businessProfile.positioning}
              onChange={(event) => setBusinessProfile({ ...businessProfile, positioning: event.target.value })}
            />

            <textarea
              className="min-h-28 rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-white outline-none"
              placeholder="Business goals"
              value={businessProfile.goals}
              onChange={(event) => setBusinessProfile({ ...businessProfile, goals: event.target.value })}
            />
          </div>
        </section>
'''

if "BUSINESS PROFILE INTELLIGENCE" not in text:
    marker = '<section className="rounded-3xl border border-white/10 bg-white/[0.04] p-6 shadow-2xl">'
    index = text.find(marker)

    if index == -1:
        raise SystemExit("ERROR: Could not find insertion marker in client page.")

    text = text[:index] + panel + "\n\n" + text[index:]

PAGE.write_text(text, encoding="utf-8")

print("STEP_267B_VISIBLE_BUSINESS_PROFILE_PANEL_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {PAGE}")
print("STEP_267B_OK")