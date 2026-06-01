from pathlib import Path

p = Path("frontend/src/app/admin/live-execution/page.tsx")
text = p.read_text(encoding="utf-8")

old = '''  const assetCandidates = [
    adapter?.asset_url,
    adapter?.image_url,
    adapter?.video_url,
    result?.asset_url,
    result?.image_url,
    result?.video_url,
    result?.media_url,
  ].filter(Boolean);'''

new = '''  const assetCandidates = [
    normalizedResult?.previewUrl,
    ...(Array.isArray(normalizedResult?.generatedFiles) ? normalizedResult.generatedFiles : []),
    adapter?.asset_url,
    adapter?.image_url,
    adapter?.video_url,
    adapter?.preview_url,
    adapter?.media_url,
    result?.asset_url,
    result?.image_url,
    result?.video_url,
    result?.media_url,
    result?.preview_url,
  ].filter(Boolean);'''

text = text.replace(old, new)

old2 = '''{assetCandidates.map((asset: string) => (
                      <a key={asset} href={asset} target="_blank" rel="noreferrer" style={{ display: "block", color: "#bfdbfe", fontWeight: 900, marginBottom: 8, wordBreak: "break-all" }}>
                        Open generated asset
                      </a>
                    ))}'''

new2 = '''{assetCandidates.map((asset: string) => (
                      <div key={asset} style={{ marginBottom: 14 }}>
                        <img src={asset} alt="Generated UGC visual asset" style={{ width: "100%", maxHeight: 360, objectFit: "contain", borderRadius: 16, border: "1px solid rgba(125,211,252,.25)", background: "#020617" }} />
                        <a href={asset} target="_blank" rel="noreferrer" style={{ display: "block", color: "#bfdbfe", fontWeight: 900, marginTop: 8, wordBreak: "break-all" }}>
                          Open generated asset
                        </a>
                      </div>
                    ))}'''

text = text.replace(old2, new2)

p.write_text(text, encoding="utf-8")
print("ADMIN_MEDIA_ASSET_PREVIEW_RENDERING_FIXED")