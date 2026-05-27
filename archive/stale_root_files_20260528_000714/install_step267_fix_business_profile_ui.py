from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")

client_page = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
backup_dir = ROOT / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

original = client_page.read_text(encoding="utf-8")

backup_file = backup_dir / f"client_page_before_step267_fix_{timestamp}.tsx"
backup_file.write_text(original, encoding="utf-8")

required_state = """
  const [businessProfile, setBusinessProfile] = useState({
    niche: "",
    products_services: "",
    target_audience: "",
    competitors: "",
    offers: "",
    brand_voice: "",
    positioning: "",
    goals: ""
  });

"""

if "const [businessProfile, setBusinessProfile]" not in original:
    marker = 'const [selectedAgents, setSelectedAgents] = useState<string[]>([]);'

    if marker in original:
        original = original.replace(
            marker,
            marker + "\n" + required_state
        )

panel = """
      {/* PREMIUM BUSINESS PROFILE PANEL */}

      <div className="rounded-2xl border border-white/10 bg-white/5 p-6 mb-6">
        <div className="text-2xl font-semibold text-white mb-2">
          Business Profile Intelligence
        </div>

        <div className="text-sm text-zinc-400 mb-6">
          Help your AI agents generate more accurate, premium-quality ecommerce outputs.
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

          <textarea
            placeholder="Business niche"
            value={businessProfile.niche}
            onChange={(e) =>
              setBusinessProfile({
                ...businessProfile,
                niche: e.target.value
              })
            }
            className="rounded-xl bg-black/30 border border-white/10 p-3 text-white min-h-[100px]"
          />

          <textarea
            placeholder="Products and services"
            value={businessProfile.products_services}
            onChange={(e) =>
              setBusinessProfile({
                ...businessProfile,
                products_services: e.target.value
              })
            }
            className="rounded-xl bg-black/30 border border-white/10 p-3 text-white min-h-[100px]"
          />

          <textarea
            placeholder="Target audience"
            value={businessProfile.target_audience}
            onChange={(e) =>
              setBusinessProfile({
                ...businessProfile,
                target_audience: e.target.value
              })
            }
            className="rounded-xl bg-black/30 border border-white/10 p-3 text-white min-h-[100px]"
          />

          <textarea
            placeholder="Competitors"
            value={businessProfile.competitors}
            onChange={(e) =>
              setBusinessProfile({
                ...businessProfile,
                competitors: e.target.value
              })
            }
            className="rounded-xl bg-black/30 border border-white/10 p-3 text-white min-h-[100px]"
          />

          <textarea
            placeholder="Offers and promotions"
            value={businessProfile.offers}
            onChange={(e) =>
              setBusinessProfile({
                ...businessProfile,
                offers: e.target.value
              })
            }
            className="rounded-xl bg-black/30 border border-white/10 p-3 text-white min-h-[100px]"
          />

          <textarea
            placeholder="Brand voice and tone"
            value={businessProfile.brand_voice}
            onChange={(e) =>
              setBusinessProfile({
                ...businessProfile,
                brand_voice: e.target.value
              })
            }
            className="rounded-xl bg-black/30 border border-white/10 p-3 text-white min-h-[100px]"
          />

          <textarea
            placeholder="Market positioning"
            value={businessProfile.positioning}
            onChange={(e) =>
              setBusinessProfile({
                ...businessProfile,
                positioning: e.target.value
              })
            }
            className="rounded-xl bg-black/30 border border-white/10 p-3 text-white min-h-[100px]"
          />

          <textarea
            placeholder="Business goals"
            value={businessProfile.goals}
            onChange={(e) =>
              setBusinessProfile({
                ...businessProfile,
                goals: e.target.value
              })
            }
            className="rounded-xl bg-black/30 border border-white/10 p-3 text-white min-h-[100px]"
          />

        </div>
      </div>
"""

if "PREMIUM BUSINESS PROFILE PANEL" not in original:

    insert_marker = '<div className="space-y-6">'

    if insert_marker in original:
        original = original.replace(
            insert_marker,
            insert_marker + "\n" + panel
        )

client_page.write_text(original, encoding="utf-8")

print("STEP_267_FIX_BUSINESS_PROFILE_UI_INSTALLED")
print(f"Backup: {backup_file}")
print(f"Updated: {client_page}")