from pathlib import Path
from datetime import datetime
import shutil

p = Path("frontend/src/app/client/page.tsx")
backup = Path("backups") / f"client_visible_outcome_typecheck_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(p, backup / "page.tsx")

s = p.read_text(encoding="utf-8")

old = '''  const selectedAsset = attachedAssets[selectedAssetIndex] || attachedAssets[0] || null;
    const visibleClientOutcomeText =
    liveDeliverable?.output ||
    liveDeliverable?.generated_output ||
    liveDeliverable?.provider_output ||
    liveDeliverable?.content ||
    liveDeliverable?.summary ||
    liveDeliverable?.message ||
    "";

'''

new = '''  const selectedAsset = attachedAssets[selectedAssetIndex] || attachedAssets[0] || null;
  const liveDeliverableAny = (liveDeliverable || {}) as any;
  const visibleClientOutcomeText =
    liveDeliverableAny?.output ||
    liveDeliverableAny?.generated_output ||
    liveDeliverableAny?.provider_output ||
    liveDeliverableAny?.content ||
    liveDeliverableAny?.summary ||
    liveDeliverableAny?.message ||
    "";

'''

if old not in s:
    raise SystemExit("Target block not found. No changes made.")

s = s.replace(old, new)

p.write_text(s, encoding="utf-8")

print("CLIENT_VISIBLE_OUTCOME_TYPECHECK_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {p}")