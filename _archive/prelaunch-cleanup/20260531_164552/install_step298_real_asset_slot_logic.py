from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
API_FILE = ROOT / "frontend" / "src" / "app" / "api" / "run-agent" / "route.ts"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

text = PAGE.read_text(encoding="utf-8")
backup = BACKUPS / f"client_page_before_step298_real_asset_slot_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

needle = '''              <div
                style={{
                  minHeight: 185,'''.strip()

start = text.find(needle)
if start == -1:
    raise SystemExit("ERROR: Asset visual block start not found.")

end_marker = '''              </div>

              <div>'''
end = text.find(end_marker, start)
if end == -1:
    raise SystemExit("ERROR: Asset visual block end not found.")

end = end + len("              </div>")

new_block = '''              <div
                style={{
                  minHeight: 185,
                  borderRadius: 18,
                  background: "#f8fafc",
                  border: "1px solid #e5eaf2",
                  position: "relative",
                  overflow: "hidden",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                {liveDeliverable?.image_url ? (
                  <img
                    src={liveDeliverable.image_url}
                    alt={liveDeliverable?.title || "Generated campaign asset"}
                    style={{
                      width: "100%",
                      height: "100%",
                      objectFit: "cover",
                      display: "block",
                    }}
                  />
                ) : (
                  <div
                    style={{
                      textAlign: "center",
                      padding: 22,
                      color: "#64748b",
                    }}
                  >
                    <div
                      style={{
                        width: 62,
                        height: 62,
                        borderRadius: 20,
                        margin: "0 auto 14px",
                        background: "linear-gradient(135deg,#eff6ff,#dbeafe)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        color: "#2563eb",
                        fontSize: 26,
                        fontWeight: 900,
                      }}
                    >
                      ✦
                    </div>

                    <div
                      style={{
                        color: "#0f172a",
                        fontWeight: 900,
                        fontSize: 14,
                        marginBottom: 5,
                      }}
                    >
                      Asset preview slot
                    </div>

                    <div
                      style={{
                        fontSize: 12,
                        lineHeight: 1.45,
                      }}
                    >
                      Generated product images, creative previews, or uploaded brand assets will appear here.
                    </div>
                  </div>
                )}
              </div>'''

text = text[:start] + new_block + text[end:]

PAGE.write_text(text, encoding="utf-8")

api = API_FILE.read_text(encoding="utf-8")
api_backup = BACKUPS / f"run_agent_route_before_step298_real_asset_slot_{timestamp}.ts"
api_backup.write_text(api, encoding="utf-8")

api = api.replace(
'''        tags: [
          "Live output",
          titleCaseAgent(primaryAgent),
          "Approval required",
          "Client-ready",
        ],''',
'''        image_url: "",
        tags: [
          "Live output",
          titleCaseAgent(primaryAgent),
          "Approval required",
          "Client-ready",
        ],'''
)

API_FILE.write_text(api, encoding="utf-8")

print("STEP_298_REAL_ASSET_SLOT_LOGIC_INSTALLED")
print(f"Page backup: {backup}")
print(f"API backup: {api_backup}")
print("STEP_298_OK")