from pathlib import Path
from datetime import datetime
import shutil

TARGET = Path("frontend/src/app/page.tsx")
content = TARGET.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

backup_file = backup_dir / f"homepage_before_testimonials_polish_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup_file)

old = '''const TESTIMONIALS = [
  { name: "Sofia Chen", role: "Founder @ NovaBrand", text: "Nexus replaced our entire creative department. We generate campaign assets in seconds that used to take 3 weeks.", stars: 5 },
  { name: "Marcus Webb", role: "Head of Content, Stripe", text: "The agents are scarily good. Aria produced a product video better than anything our agency made at 10x the cost.", stars: 5 },
  { name: "Priya Nair", role: "Solo creator, 2.1M followers", text: "I went from 3 videos a month to 60. My engagement is up 380%. Nexus is the unfair advantage I needed.", stars: 5 },
  { name: "Lucas Ferreira", role: "CMO @ ShopCloud", text: "Our whole team is 2 people now. Nexus handles everything else. This is how startups should operate in 2026.", stars: 5 },
  { name: "Aiko Tanaka", role: "Video Director", text: "The Cinema Engine is unreal — Hollywood-grade visuals, 8 seconds, no renders. I feel like I have a GPU farm in my browser.", stars: 5 },
  { name: "James Oduya", role: "Growth Lead, Linear", text: "We shipped 3 full ad campaigns in one afternoon. Our CPM dropped 42%. Nexus pays for itself in day one.", stars: 5 },
];'''

new = '''const TESTIMONIALS = [
  { name: "Sofia Chen", role: "Founder, premium skincare brand", text: "The platform gives us a governed ecommerce team we can actually use daily — product content, support, campaign ideas and execution all stay aligned to our brand.", stars: 5 },
  { name: "Marcus Webb", role: "Operations Lead, Shopify retailer", text: "The biggest difference is control. Our agents can prepare real work, but approvals protect spend, scaling and customer-facing actions.", stars: 5 },
  { name: "Priya Nair", role: "Growth Manager, fashion ecommerce", text: "We moved from scattered AI tools to one workspace that understands our products, competitors, audience and market positioning.", stars: 5 },
  { name: "Lucas Ferreira", role: "Owner, multi-product store", text: "It feels like adding a senior digital team without hiring one. The outputs are commercially useful, not generic prompts dressed up as automation.", stars: 5 },
  { name: "Aiko Tanaka", role: "Creative Director, DTC brand", text: "UGC briefs, product angles, ad concepts and landing page direction now come from the same business context instead of disconnected tools.", stars: 5 },
  { name: "James Oduya", role: "Head of Growth, ecommerce group", text: "Governed execution is the reason we trust it. The system helps us move faster without giving AI uncontrolled authority over spend or scaling.", stars: 5 },
];'''

if old not in content:
    raise RuntimeError("Original TESTIMONIALS block not found.")

content = content.replace(old, new)

replacements = {
    "Creators love Nexus.": "Built for serious ecommerce operators.",
    "Deploy your AI workforce<br />in days, not months.": "Launch a premium AI workforce<br />for your ecommerce business.",
    "Enterprise-grade governance · Scalable AI operations · Owner-controlled execution": "Premium ecommerce outputs · Governed live execution · Owner-controlled growth",
    "Launch your workforce": "Start building",
    "Schedule strategy call": "Talk to support",
}

for old_text, new_text in replacements.items():
    content = content.replace(old_text, new_text)

TARGET.write_text(content, encoding="utf-8")

print("HOMEPAGE_TESTIMONIALS_POLISHED")
print("Backup:", backup_file)