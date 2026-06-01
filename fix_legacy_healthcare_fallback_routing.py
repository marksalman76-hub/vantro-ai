from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "runtime" / "intelligent_action_packet_normalizer.py"

BACKUP = ROOT / "backups" / f"legacy_healthcare_fallback_cleanup_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / "intelligent_action_packet_normalizer.py")

s = TARGET.read_text(encoding="utf-8")

old = '''    if "marketing" in lower or "thought" in lower or "content" in lower:
        return "Create healthcare technology thought leadership content calendar and first asset briefs"'''

new = '''    if "seo" in lower or "search" in lower or "meta description" in lower or "organic" in lower:
        return "Create SEO optimisation deliverables and metadata"

    if "marketing" in lower or "thought leadership" in lower or "content calendar" in lower:
        return "Create marketing campaign content deliverables"'''

if old not in s:
    raise SystemExit("Could not find legacy healthcare fallback block.")

s = s.replace(old, new)

# Remove legacy healthcare default fallback contamination.
s = s.replace(
'''    return "Create executable implementation checklist from approved healthcare technology strategy"''',
'''    return "Create executable implementation deliverable from approved autonomous task request"'''
)

TARGET.write_text(s, encoding="utf-8")

print("LEGACY_HEALTHCARE_FALLBACK_ROUTING_FIXED")
print("Backup:", BACKUP)
print("Updated:", TARGET)