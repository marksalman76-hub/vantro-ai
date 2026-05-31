from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"page_before_footer_anchor_targets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(PAGE, backup)

s = PAGE.read_text(encoding="utf-8")

# Add real anchor targets to current landing sections.
section_targets = [
    ("platform", ['className="platform"', 'className="platform-section"', 'className="hero"', 'className="section section--platform"']),
    ("agents", ['className="agents"', 'className="agents-section"', 'className="section section--agents"']),
    ("studio", ['className="studio"', 'className="creation-studio"', 'className="section section--studio"']),
    ("features", ['className="features"', 'className="feature-bento"', 'className="section section--features"']),
    ("workflow", ['className="workflow"', 'className="workflow-section"', 'className="section section--workflow"']),
    ("pricing", ['className="pricing"', 'className="pricing-section"', 'className="section section--pricing"']),
]

for target_id, markers in section_targets:
    if f'id="{target_id}"' in s:
        continue
    for marker in markers:
        if marker in s:
            s = s.replace(marker, f'id="{target_id}" {marker}', 1)
            break

# If any targets still do not exist, add invisible anchors before footer.
missing = [target for target, _ in section_targets if f'id="{target}"' not in s]
if missing:
    anchors = "\n".join([f'<div id="{target}" style={{ scrollMarginTop: 120 }} />' for target in missing])
    footer_marker = "<footer"
    if footer_marker in s:
        s = s.replace(footer_marker, anchors + "\n      " + footer_marker, 1)

# Make internal anchors scroll below sticky nav.
if "html { scroll-behavior: smooth;" not in s and "<style" in s:
    s = s.replace(
        "<style",
        "<style",
        1,
    )

if "scroll-margin-top: 120px" not in s:
    css = '''
        html { scroll-behavior: smooth; }
        section[id], div[id] { scroll-margin-top: 120px; }
'''
    marker = "</style>"
    if marker in s:
        s = s.replace(marker, css + "\n      " + marker, 1)

PAGE.write_text(s, encoding="utf-8")

print("LANDING_FOOTER_ANCHOR_TARGETS_FIXED")
print(f"Backup: {backup}")