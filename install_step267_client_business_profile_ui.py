from pathlib import Path
from datetime import datetime
import py_compile

ROOT = Path.cwd()
CLIENT_PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
TEST = ROOT / "test_step267_client_business_profile_ui.py"
BACKUPS = ROOT / "backups"

BACKUPS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUPS / f"client_page_before_step267_{timestamp}.tsx"
backup.write_text(CLIENT_PAGE.read_text(encoding="utf-8"), encoding="utf-8")

text = CLIENT_PAGE.read_text(encoding="utf-8")

text = text.replace(
    'const [task, setTask] = useState("Create a premium ecommerce output for my store.");',
    '''const [task, setTask] = useState("Create a premium ecommerce output for my store.");
  const [businessProfile, setBusinessProfile] = useState({
    niche: "",
    products: "",
    audience: "",
    competitors: "",
    offers: "",
    margins: "",
    regions: "",
    brandTone: "",
    goals: "",
  });'''
)

profile_panel = '''
          <section
            style={{
              marginTop: 24,
              padding: 22,
              borderRadius: 22,
              background: "rgba(15,23,42,.82)",
              border: "1px solid rgba(148,163,184,.14)",
            }}
          >
            <h2 style={{ margin: 0, fontSize: 28 }}>Business Profile</h2>
            <p style={{ color: "#94a3b8", lineHeight: 1.7 }}>
              Add business context so agents can produce sharper, more relevant, conversion-focused outputs.
            </p>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit,minmax(240px,1fr))",
                gap: 12,
              }}
            >
              {[
                ["niche", "Niche / category"],
                ["products", "Products / services"],
                ["audience", "Target audience"],
                ["competitors", "Competitors"],
                ["offers", "Current offers"],
                ["margins", "Margins / pricing notes"],
                ["regions", "Regions / countries"],
                ["brandTone", "Brand tone"],
                ["goals", "Main goals"],
              ].map(([key, label]) => (
                <label key={key} style={{ display: "grid", gap: 6, color: "#cbd5e1" }}>
                  <span style={{ fontSize: 13 }}>{label}</span>
                  <textarea
                    value={(businessProfile as any)[key]}
                    onChange={(event) =>
                      setBusinessProfile((current) => ({
                        ...current,
                        [key]: event.target.value,
                      }))
                    }
                    rows={3}
                    style={{
                      width: "100%",
                      padding: 12,
                      borderRadius: 12,
                      background: "#020617",
                      color: "#fff",
                      border: "1px solid rgba(148,163,184,.22)",
                      resize: "vertical",
                    }}
                  />
                </label>
              ))}
            </div>
          </section>

'''

anchor = '''          <section
            style={{
              marginTop: 24,
              padding: 22,'''

if "Business Profile" not in text:
    text = text.replace(anchor, profile_panel + anchor, 1)

text = text.replace(
    '''body: JSON.stringify({
            requested_agent: agentId,
            task,
          }),''',
    '''body: JSON.stringify({
            requested_agent: agentId,
            task,
            business_profile: businessProfile,
          }),'''
)

CLIENT_PAGE.write_text(text, encoding="utf-8")

TEST.write_text(r'''
from pathlib import Path
import subprocess

ROOT = Path.cwd()
client_page = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
text = client_page.read_text(encoding="utf-8", errors="ignore").lower()

checks = {
    "client_page_exists": client_page.exists(),
    "business_profile_panel_present": "business profile" in text,
    "niche_field_present": "niche / category" in text,
    "products_field_present": "products / services" in text,
    "audience_field_present": "target audience" in text,
    "competitors_field_present": "competitors" in text,
    "offers_field_present": "current offers" in text,
    "regions_field_present": "regions / countries" in text,
    "brand_tone_field_present": "brand tone" in text,
    "goals_field_present": "main goals" in text,
    "business_profile_sent_to_run_agent": "business_profile: businessprofile" in text,
}

print("STEP_267_CLIENT_BUSINESS_PROFILE_UI_RESULTS")
for name, passed in checks.items():
    print(name, passed)

failed = [name for name, passed in checks.items() if not passed]

print("RUNNING_FRONTEND_BUILD")
build = subprocess.run(["npm.cmd", "run", "build"], cwd=str(ROOT / "frontend"), text=True)
print("frontend_build_exit_code", build.returncode)

if build.returncode != 0:
    failed.append("frontend_build")

if failed:
    print("FAILED", failed)
    raise SystemExit(1)

print("STEP_267_CLIENT_BUSINESS_PROFILE_UI_OK")
'''.lstrip(), encoding="utf-8")

py_compile.compile(str(TEST), doraise=True)

print("STEP_267_CLIENT_BUSINESS_PROFILE_UI_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {CLIENT_PAGE}")
print(f"Created/updated: {TEST}")
print("STEP_267_OK")