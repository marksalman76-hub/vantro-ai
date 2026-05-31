from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step296_premium_output_visual_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

old = '''              <div
                style={{
                  minHeight: 185,
                  borderRadius: 16,
                  background: "linear-gradient(135deg,#e8d5bd,#b9874f,#fff4df)",
                }}
              />'''

new = '''              <div
                style={{
                  minHeight: 185,
                  borderRadius: 18,
                  background:
                    "radial-gradient(circle at 28% 24%, rgba(255,255,255,.95), rgba(255,255,255,0) 26%), linear-gradient(135deg,#f8ead8 0%,#d7aa70 38%,#9b6a3c 70%,#f6dfbd 100%)",
                  position: "relative",
                  overflow: "hidden",
                  boxShadow: "inset 0 0 0 1px rgba(255,255,255,.45)",
                }}
              >
                <div
                  style={{
                    position: "absolute",
                    inset: 18,
                    borderRadius: 16,
                    border: "1px solid rgba(255,255,255,.48)",
                    background:
                      "linear-gradient(135deg,rgba(255,255,255,.22),rgba(255,255,255,.04))",
                  }}
                />

                <div
                  style={{
                    position: "absolute",
                    left: "50%",
                    top: "50%",
                    transform: "translate(-50%,-43%)",
                    width: 112,
                    height: 112,
                    borderRadius: 28,
                    background:
                      "linear-gradient(145deg,rgba(255,255,255,.92),rgba(241,211,170,.92))",
                    boxShadow: "0 22px 55px rgba(91,54,24,.22)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    textAlign: "center",
                    color: "#7c4a1f",
                    fontWeight: 900,
                    letterSpacing: 1.2,
                    fontSize: 15,
                  }}
                >
                  LUXE
                  <br />
                  LAUNCH
                </div>

                <div
                  style={{
                    position: "absolute",
                    left: 22,
                    bottom: 20,
                    right: 22,
                    color: "#fffaf0",
                    fontWeight: 900,
                    textShadow: "0 2px 12px rgba(0,0,0,.22)",
                    fontSize: 14,
                    lineHeight: 1.35,
                  }}
                >
                  Premium campaign preview
                </div>
              </div>'''

if old not in text:
    raise SystemExit("ERROR: Output image placeholder block not found.")

text = text.replace(old, new)

PAGE.write_text(text, encoding="utf-8")

print("STEP_296_PREMIUM_OUTPUT_VISUAL_INSTALLED")
print(f"Backup: {backup}")
print("STEP_296_OK")