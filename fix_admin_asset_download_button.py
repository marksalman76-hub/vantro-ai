from pathlib import Path

p = Path("frontend/src/app/admin/live-execution/page.tsx")
text = p.read_text(encoding="utf-8")

text = text.replace(
'''<a href={asset} download={`ugc-visual-asset-${Date.now()}.svg`} style={{ display: "block", color: "#bfdbfe", fontWeight: 900, marginTop: 8, wordBreak: "break-all" }}>
                          Download generated asset
                        </a>''',
'''<button
                          type="button"
                          onClick={() => {
                            const a = document.createElement("a");
                            a.href = asset;
                            a.download = `ugc-visual-asset-${Date.now()}.svg`;
                            document.body.appendChild(a);
                            a.click();
                            a.remove();
                          }}
                          style={{ display: "block", width: "100%", border: "1px solid rgba(125,211,252,.3)", background: "#020617", color: "#bfdbfe", fontWeight: 900, marginTop: 8, padding: "10px 12px", borderRadius: 12, cursor: "pointer" }}
                        >
                          Download generated asset
                        </button>'''
)

p.write_text(text, encoding="utf-8")
print("ADMIN_ASSET_DOWNLOAD_BUTTON_FIXED")