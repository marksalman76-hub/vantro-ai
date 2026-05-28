from pathlib import Path
from datetime import datetime
import shutil
import re

p = Path("frontend/src/app/client/page.tsx")
backup = Path("backups") / f"client_visible_outcome_insert_fix_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(p, backup / "page.tsx")

s = p.read_text(encoding="utf-8")

bad_block = '''  const visibleClientOutcomeText =
    liveDeliverable?.output ||
    liveDeliverable?.generated_output ||
    liveDeliverable?.provider_output ||
    liveDeliverable?.content ||
    liveDeliverable?.summary ||
    liveDeliverable?.message ||
    "";
'''

s = s.replace(bad_block, "")

marker = "const reviewStatus"
idx = s.find(marker)
if idx == -1:
    marker = "const primaryAssetUrl"
    idx = s.find(marker)

if idx == -1:
    raise SystemExit("Could not find safe insertion marker.")

insert = '''  const visibleClientOutcomeText =
    liveDeliverable?.output ||
    liveDeliverable?.generated_output ||
    liveDeliverable?.provider_output ||
    liveDeliverable?.content ||
    liveDeliverable?.summary ||
    liveDeliverable?.message ||
    "";

'''

s = s[:idx] + insert + s[idx:]

p.write_text(s, encoding="utf-8")

print("CLIENT_VISIBLE_OUTCOME_INSERT_LOCATION_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {p}")