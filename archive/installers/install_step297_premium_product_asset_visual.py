from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step297_product_asset_visual_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

start = text.find('''              <div
                style={{
                  minHeight: 185,
                  borderRadius: 18,
                  background:
                    "radial-gradient(circle at 28% 24%, rgba(255,255,255,.95), rgba(255,255,255,0) 26%), linear-gradient(135deg,#f8ead8 0%,#d7aa70 38%,#9b6a3c 70%,#f6dfbd 100%)",''')

if start == -1:
    raise SystemExit("ERROR: Existing premium visual block not found.")

end_marker = '''              </div>

              <div>'''
end = text.find(end_marker, start)

if end == -1:
    raise SystemExit("ERROR: Existing premium visual block end not found.")

new_visual = '''              <div
                style={{
                  minHeight: 185,
                  borderRadius: 18,
                  background:
                    "radial-gradient(circle at 30% 20%, rgba(255,255,255,.9), rgba(255,255,255,0) 24%), linear-gradient(135deg,#fff7ed 0%,#ecd2aa 36%,#c58a4a 72%,#fff1d6 100%)",
                  position: "relative",
                  overflow: "hidden",
                  boxShadow: "inset 0 0 0 1px rgba(255,255,255,.6)",
                }}
              >
                <div
                  style={{
                    position: "absolute",
                    inset: 0,
                    background:
                      "linear-gradient(120deg,rgba(255,255,255,.34),rgba(255,255,255,0) 42%,rgba(120,53,15,.12))",
                  }}
                />

                <div
                  style={{
                    position: "absolute",
                    left: 30,
                    right: 30,
                    bottom: 24,
                    height: 28,
                    borderRadius: "50%",
                    background: "rgba(90,48,18,.18)",
                    filter: "blur(10px)",
                  }}
                />

                <div
                  style={{
                    position: "absolute",
                    left: "50%",
                    top: "49%",
                    transform: "translate(-50%,-50%)",
                    width: 118,
                    height: 126,
                    borderRadius: "26px 26px 34px 34px",
                    background:
                      "linear-gradient(145deg,#fffaf2 0%,#f3d9b5 46%,#c78b4b 100%)",
                    boxShadow:
                      "0 22px 42px rgba(91,54,24,.22), inset 0 1px 0 rgba(255,255,255,.75)",
                    border: "1px solid rgba(255,255,255,.72)",
                  }}
                >
                  <div
                    style={{
                      position: "absolute",
                      left: 20,
                      right: 20,
                      top: -14,
                      height: 30,
                      borderRadius: 999,
                      background:
                        "linear-gradient(180deg,#fef3c7,#b77935)",
                      boxShadow: "0 8px 18px rgba(91,54,24,.18)",
                      border: "1px solid rgba(255,255,255,.6)",
                    }}
                  />

                  <div
                    style={{
                      position: "absolute",
                      left: 18,
                      right: 18,
                      top: 42,
                      height: 46,
                      borderRadius: 14,
                      background: "rgba(255,255,255,.58)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      color: "#7c4a1f",
                      fontWeight: 900,
                      fontSize: 13,
                      letterSpacing: 1.1,
                    }}
                  >
                    LUXE
                  </div>
                </div>

                <div
                  style={{
                    position: "absolute",
                    right: 22,
                    top: 22,
                    width: 52,
                    height: 52,
                    borderRadius: 18,
                    background: "rgba(255,255,255,.52)",
                    border: "1px solid rgba(255,255,255,.65)",
                    boxShadow: "0 14px 28px rgba(91,54,24,.10)",
                  }}
                />

                <div
                  style={{
                    position: "absolute",
                    left: 22,
                    top: 26,
                    width: 12,
                    height: 12,
                    borderRadius: 999,
                    background: "rgba(255,255,255,.82)",
                    boxShadow: "28px 42px 0 rgba(255,255,255,.35)",
                  }}
                />
              </div>'''

text = text[:start] + new_visual + text[end:]

PAGE.write_text(text, encoding="utf-8")

print("STEP_297_PREMIUM_PRODUCT_ASSET_VISUAL_INSTALLED")
print(f"Backup: {backup}")
print("STEP_297_OK")