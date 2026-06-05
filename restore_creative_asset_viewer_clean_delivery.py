from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
PAGE = ROOT / "frontend/src/app/admin/creative-assets/page.tsx"
BACKUP = ROOT / "backups" / f"creative_asset_viewer_clean_delivery_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(PAGE, BACKUP / "page.tsx")

text = PAGE.read_text(encoding="utf-8", errors="ignore")
original = text

# Add helper functions after imports / before component logic if not already present.
helper = r'''
function cleanAssetReference(value: any): string {
  const text = String(value || "");
  if (!text) return "";
  if (text.startsWith("data:")) return "Embedded generated asset reference hidden for clean admin display.";
  if (text.length > 320) return text.slice(0, 320) + "...";
  return text;
}

function isHugeEmbeddedAsset(value: any): boolean {
  const text = String(value || "");
  return text.startsWith("data:") || text.length > 1200;
}

function cleanAssetContent(value: any): string {
  const text = String(value || "");
  if (!text) return "";
  if (text.startsWith("{") && text.includes('"content"')) {
    try {
      const parsed = JSON.parse(text);
      return String(parsed.content || parsed.summary || parsed.asset_content || text);
    } catch {
      return text;
    }
  }
  return text;
}
'''

if "function cleanAssetReference" not in text:
    # Insert after "use client" block/imports safely.
    marker = 'import'
    first_import = text.find(marker)
    if first_import >= 0:
        # Insert after final import line.
        lines = text.splitlines()
        insert_at = 0
        for i, line in enumerate(lines):
            if line.startswith("import "):
                insert_at = i + 1
        lines.insert(insert_at, helper)
        text = "\n".join(lines) + "\n"
    else:
        text = helper + "\n" + text

# Hide huge original provider/reference blocks.
text = text.replace(
    '''<p>{asset.original_provider_url || asset.originalProviderUrl || asset.provider_url || asset.providerUrl || "—"}</p>''',
    '''<p>{cleanAssetReference(asset.original_provider_url || asset.originalProviderUrl || asset.provider_url || asset.providerUrl || "—")}</p>'''
)

text = text.replace(
    '''{asset.original_provider_url || asset.originalProviderUrl || asset.provider_url || asset.providerUrl || "—"}''',
    '''{cleanAssetReference(asset.original_provider_url || asset.originalProviderUrl || asset.provider_url || asset.providerUrl || "—")}'''
)

# Replace raw content rendering if present.
text = text.replace(
    '''{asset.content || asset.asset_content || asset.summary || ""}''',
    '''{cleanAssetContent(asset.content || asset.asset_content || asset.summary || "")}'''
)

# Add CSS-friendly class hints for broken / text fallback cards if common image tag exists.
text = text.replace(
    '''<img src={asset.preview_url || asset.previewUrl || asset.url}''',
    '''<img onError={(event) => { (event.currentTarget as HTMLImageElement).style.display = "none"; }} src={asset.preview_url || asset.previewUrl || asset.url}'''
)

# Add a clean fallback message before card actions if no visual media exists.
fallback_marker = '''<button className="assetButton"'''
fallback_block = '''{(!asset.preview_url && !asset.previewUrl && !asset.url && (asset.content || asset.asset_content || asset.summary)) ? (
                  <div className="assetTextPreview">
                    <strong>Generated text asset</strong>
                    <p>{cleanAssetContent(asset.content || asset.asset_content || asset.summary)}</p>
                  </div>
                ) : null}

                <button className="assetButton"'''
if "assetTextPreview" not in text and fallback_marker in text:
    text = text.replace(fallback_marker, fallback_block, 1)

# If class names differ, add generic minimal styles before final style close if style block exists.
style = r'''
        .assetTextPreview {
          margin-top: 12px;
          padding: 12px;
          border: 1px solid rgba(148, 163, 184, 0.22);
          border-radius: 12px;
          background: rgba(15, 23, 42, 0.72);
          color: #e5e7eb;
          white-space: pre-wrap;
          max-height: 220px;
          overflow: auto;
        }
        .assetTextPreview strong {
          display: block;
          margin-bottom: 6px;
          color: #67e8f9;
        }
        .assetTextPreview p {
          margin: 0;
          color: #cbd5e1;
          font-size: 12px;
          line-height: 1.5;
        }
'''
if ".assetTextPreview" not in text and "</style>" in text:
    text = text.replace("</style>", style + "\n      </style>", 1)

PAGE.write_text(text, encoding="utf-8", newline="\n")

if text == original:
    print("NO_CHANGE_CREATIVE_ASSET_VIEWER_ALREADY_CLEAN")
else:
    print("CREATIVE_ASSET_VIEWER_CLEAN_DELIVERY_RESTORED")
    print(f"Backup: {BACKUP}")