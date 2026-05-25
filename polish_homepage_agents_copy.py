from pathlib import Path
from datetime import datetime
import shutil

TARGET = Path("frontend/src/app/page.tsx")
content = TARGET.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup_file = backup_dir / f"homepage_before_agents_copy_polish_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup_file)

replacements = {
    '{ value: "2.1M+",  label: "Creators worldwide",    icon: Globe  },':
    '{ value: "24/7",   label: "AI workforce coverage", icon: Globe  },',

    '{ value: "180M+",  label: "Assets generated",       icon: Layers },':
    '{ value: "22+",    label: "Specialist agent roles", icon: Layers },',

    '{ value: "99.97%", label: "Uptime SLA",             icon: Shield },':
    '{ value: "100%",   label: "Governed execution flow", icon: Shield },',

    '{ value: "< 8s",   label: "Avg. generation time",   icon: Clock  },':
    '{ value: "Global", label: "Market-aware outputs",   icon: Clock  },',

    'Meet your new<br />dream team.':
    'Your ecommerce<br />AI workforce.',

    'Specialized agents. One shared brain. Infinite output.':
    'Specialised agents for content, support, analytics, product growth and governed live execution.',

    'Explore all agents <ChevronRight size={14} />':
    'View workforce catalogue <ChevronRight size={14} />',

    '<a href="#" className="btn-outline">':
    '<a href="#pricing" className="btn-outline">',
}

for old, new in replacements.items():
    if old not in content:
        print("WARNING missing:", old[:80])
    content = content.replace(old, new)

TARGET.write_text(content, encoding="utf-8")

print("HOMEPAGE_AGENTS_COPY_POLISHED")
print("Backup:", backup_file)