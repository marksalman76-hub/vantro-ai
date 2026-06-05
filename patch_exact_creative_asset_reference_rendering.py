from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
PAGE = ROOT / "frontend/src/app/admin/creative-assets/page.tsx"
BACKUP = ROOT / "backups" / f"creative_asset_reference_exact_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(PAGE, BACKUP / "page.tsx")

text = PAGE.read_text(encoding="utf-8", errors="ignore")
original = text

old = '''      {asset.original_preview_url || asset.provider_asset_url ? (
        <div style={urlBoxStyle}>
          <p style={urlLabelStyle}>Original provider URL / reference</p>
          <p style={urlTextStyle}>{asset.original_preview_url || asset.provider_asset_url}</p>
          <p style={warningTextStyle}>Not used for browser playback.</p>
        </div>
      ) : null}'''

new = '''      {asset.original_preview_url || asset.provider_asset_url ? (
        <div style={urlBoxStyle}>
          <p style={urlLabelStyle}>Original provider URL / reference</p>
          <p style={urlTextStyle}>
            {isHugeEmbeddedAsset(asset.original_preview_url || asset.provider_asset_url)
              ? "Embedded generated provider reference hidden for clean admin display."
              : cleanAssetReference(asset.original_preview_url || asset.provider_asset_url)}
          </p>
          <p style={warningTextStyle}>Not used for browser playback.</p>
        </div>
      ) : null}'''

if old not in text:
    raise RuntimeError("Exact provider reference block not found")

text = text.replace(old, new, 1)
PAGE.write_text(text, encoding="utf-8", newline="\n")

print("EXACT_CREATIVE_ASSET_REFERENCE_RENDERING_PATCHED")
print(f"Backup: {BACKUP}")