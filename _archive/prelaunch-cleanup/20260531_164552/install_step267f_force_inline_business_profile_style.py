from pathlib import Path
from datetime import datetime
import re

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_step267f_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

start = text.find("BUSINESS PROFILE INTELLIGENCE")
if start == -1:
    raise SystemExit("ERROR: Business profile panel not found.")

section_start = text.rfind("<section", 0, start)
client_workspace = text.find("CLIENT WORKSPACE", start)
section_end = text.rfind("<p", 0, client_workspace)

if section_start == -1 or client_workspace == -1 or section_end == -1:
    raise SystemExit("ERROR: Could not safely locate panel boundaries.")

field_style = '{{ width: "100%", minHeight: "110px", borderRadius: "18px", border: "1px solid rgba(255,255,255,0.12)", background: "rgba(2,6,23,0.72)", color: "white", padding: "16px", fontSize: "14px", outline: "none", resize: "vertical" }}'

panel = f'''        <section className="mb-10 rounded-3xl border border-cyan-400/20 bg-cyan-400/[0.04] p-6 shadow-2xl">
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
            <textarea style={field_style} placeholder="Business niche" value={{businessProfile.niche}} onChange={{(event) => setBusinessProfile({{ ...businessProfile, niche: event.target.value }})}} />
            <textarea style={field_style} placeholder="Products and services" value={{businessProfile.products_services}} onChange={{(event) => setBusinessProfile({{ ...businessProfile, products_services: event.target.value }})}} />
            <textarea style={field_style} placeholder="Target audience" value={{businessProfile.target_audience}} onChange={{(event) => setBusinessProfile({{ ...businessProfile, target_audience: event.target.value }})}} />
            <textarea style={field_style} placeholder="Competitors" value={{businessProfile.competitors}} onChange={{(event) => setBusinessProfile({{ ...businessProfile, competitors: event.target.value }})}} />
            <textarea style={field_style} placeholder="Offers and promotions" value={{businessProfile.offers}} onChange={{(event) => setBusinessProfile({{ ...businessProfile, offers: event.target.value }})}} />
            <textarea style={field_style} placeholder="Brand voice and tone" value={{businessProfile.brand_voice}} onChange={{(event) => setBusinessProfile({{ ...businessProfile, brand_voice: event.target.value }})}} />
            <textarea style={field_style} placeholder="Market positioning" value={{businessProfile.positioning}} onChange={{(event) => setBusinessProfile({{ ...businessProfile, positioning: event.target.value }})}} />
            <textarea style={field_style} placeholder="Business goals" value={{businessProfile.goals}} onChange={{(event) => setBusinessProfile({{ ...businessProfile, goals: event.target.value }})}} />
          </div>
        </section>

'''

text = text[:section_start] + panel + text[section_end:]
PAGE.write_text(text, encoding="utf-8")

print("STEP_267F_INLINE_BUSINESS_PROFILE_STYLE_INSTALLED")
print(f"Backup: {backup}")
print("STEP_267F_OK")