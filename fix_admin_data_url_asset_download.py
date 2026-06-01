from pathlib import Path

p = Path("frontend/src/app/admin/live-execution/page.tsx")
text = p.read_text(encoding="utf-8")

old = '''<a href={asset} target="_blank" rel="noreferrer" style={{ display: "block", color: "#bfdbfe", fontWeight: 900, marginTop: 8, wordBreak: "break-all" }}>
                          Open generated asset
                        </a>'''

new = '''<a href={asset} download={`ugc-visual-asset-${Date.now()}.svg`} style={{ display: "block", color: "#bfdbfe", fontWeight: 900, marginTop: 8, wordBreak: "break-all" }}>
                          Download generated asset
                        </a>'''

text = text.replace(old, new)

p.write_text(text, encoding="utf-8")
print("ADMIN_DATA_URL_ASSET_DOWNLOAD_FIXED")