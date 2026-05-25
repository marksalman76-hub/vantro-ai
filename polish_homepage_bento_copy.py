from pathlib import Path
from datetime import datetime
import shutil

TARGET = Path("frontend/src/app/page.tsx")
content = TARGET.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

backup_file = backup_dir / f"homepage_before_bento_copy_polish_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup_file)

replacements = {
    "Everything in one orbit.":
    "One governed AI operating system.",

    "<Cpu size={14} /> SUPERCOMPUTER":
    "<Cpu size={14} /> WORKFORCE ENGINE",

    "Your agents work 24/7,<br />even while you sleep.":
    "Your AI workforce operates<br />around the clock.",

    "Autonomous scheduling, memory, connectors, and real-time automations — all orchestrated by a shared intelligence layer.":
    "Governed execution, persistent business memory, live integrations and coordinated multi-agent workflows in one platform.",

    "<Brain size={14} /> BRAIN AI":
    "<Brain size={14} /> BUSINESS MEMORY",

    "Learns your brand.<br />Thinks like you.":
    "Learns your business.<br />Adapts to your market.",

    "Upload docs, style guides, past work — your agents internalize everything.":
    "Agents adapt to your products, positioning, competitors, audience, region and operational workflows.",

    "<Video size={14} /> CINEMA ENGINE":
    "<Video size={14} /> CONTENT ENGINE",

    "4K video in under 8 seconds.":
    "Premium ecommerce content generation.",

    "Powered by Seedance 2.0 — the fastest diffusion model on the planet.":
    "UGC, product creatives, ads, landing pages and campaign assets generated through governed AI workflows.",

    "87% faster than competitors":
    "Premium-quality output generation",

    "<Globe size={14} /> INTEGRATIONS":
    "<Globe size={14} /> LIVE INTEGRATIONS",

    "200+ connectors.":
    "Connect your business stack.",

    '<span key={s} className="bento-card__badge">{s}</span>':
    '<span key={s} className="bento-card__badge">{s}</span>',

    "<Award size={14} /> MILESTONES":
    "<Award size={14} /> GOVERNANCE",

    "Level up your workflow.":
    "Owner-controlled execution.",

    "Level 12 · 7,200 XP":
    "Approval-gated scaling and protected automation"
}

for old, new in replacements.items():
    if old not in content:
        print("WARNING missing:", old[:80])
    content = content.replace(old, new)

TARGET.write_text(content, encoding="utf-8")

print("HOMEPAGE_BENTO_COPY_POLISHED")
print("Backup:", backup_file)