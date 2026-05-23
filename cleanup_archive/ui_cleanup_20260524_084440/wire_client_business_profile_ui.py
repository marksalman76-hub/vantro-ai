from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

text = PAGE.read_text(encoding="utf-8")
backup = BACKUP_DIR / f"client_page_before_business_profile_wire_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
backup.write_text(text, encoding="utf-8")

# Add profile state after execution state.
text = text.replace(
    'const [executionState, setExecutionState] = useState<"idle" | "running" | "completed" | "rejected">("idle");',
    '''const [executionState, setExecutionState] = useState<"idle" | "running" | "completed" | "rejected">("idle");
  const [businessProfile, setBusinessProfile] = useState<Record<string, string>>({});
  const [businessProfileSaved, setBusinessProfileSaved] = useState(false);'''
)

# Load profile after client-me fetch block starts.
text = text.replace(
    'fetch("/api/client-me")',
    'fetch("/api/client-me")'
)

# Insert functions before loadExecutionTimeline.
marker = "  async function loadExecutionTimeline() {"
insert = r'''
  async function loadBusinessProfile() {
    try {
      const response = await fetch("/api/client-business-profile", { cache: "no-store" });
      const data = await response.json();

      if (data?.success && data.profile) {
        setBusinessProfile(data.profile);
        setBusinessProfileSaved(Boolean(data.profile_saved));
      }
    } catch {
      setBusinessProfileSaved(false);
    }
  }

  async function saveBusinessProfile() {
    try {
      const response = await fetch("/api/client-business-profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ profile: businessProfile }),
      });

      const data = await response.json();

      if (!response.ok || !data?.success) {
        setToastMessage("Business profile could not be saved.");
        return;
      }

      setBusinessProfile(data.profile || businessProfile);
      setBusinessProfileSaved(true);
      setToastMessage("Business profile saved. Future agent runs will use this context.");
    } catch {
      setToastMessage("Business profile could not be saved.");
    }
  }

'''
if marker not in text:
    raise SystemExit("LOAD_EXECUTION_TIMELINE_MARKER_NOT_FOUND")
text = text.replace(marker, insert + marker, 1)

# Ensure loadBusinessProfile runs near existing account load useEffect by adding before loadExecutionTimeline call.
text = text.replace(
    'loadExecutionTimeline();',
    'loadBusinessProfile();\n      loadExecutionTimeline();',
    1
)

# Replace business profile textarea defaultValue with controlled values.
replacements = {
    'defaultValue={value}': 'value={businessProfile[key] || ""} onChange={(e) => setBusinessProfile((prev) => ({ ...prev, [key]: e.target.value }))}',
    'Γ£ô Applied to execution': '{businessProfileSaved ? "✓ Saved to execution context" : "Not saved yet"}',
}

for old, new in replacements.items():
    text = text.replace(old, new)

# Add save button after profile helper text if not already present.
old_block = '''Add business context once so every active AI agent can produce more accurate
                deliverables, assets, copy, positioning, and execution recommendations.
              </p>'''
new_block = '''Add business context once so every active AI agent can produce more accurate
                deliverables, assets, copy, positioning, and execution recommendations.
              </p>
              <button
                type="button"
                onClick={saveBusinessProfile}
                style={{
                  marginTop: 14,
                  border: 0,
                  borderRadius: 12,
                  padding: "12px 16px",
                  background: "var(--color-blue)",
                  color: "white",
                  fontWeight: 900,
                  cursor: "pointer",
                }}
              >
                Save business profile
              </button>'''

if old_block not in text:
    raise SystemExit("BUSINESS_PROFILE_HELPER_BLOCK_NOT_FOUND")

text = text.replace(old_block, new_block, 1)

PAGE.write_text(text, encoding="utf-8")

print("CLIENT_BUSINESS_PROFILE_UI_WIRED")
print(f"Backup: {backup}")