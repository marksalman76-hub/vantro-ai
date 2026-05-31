from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"client_page_before_current_exact_integration_block2_dark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")

# Fix integration strip segment directly.
start = s.find('<h2 style={{ margin: 0, fontSize: 16 }}>Integrations</h2>')
end = s.find('<section style={responsiveWorkspaceGridStyle}>', start)
if start == -1 or end == -1:
    raise SystemExit("FAILED: integration strip segment not found")

seg = s[start:end]
seg = seg.replace('border: "1px solid #e5eaf2",', 'border: darkModeEnabled ? "1px solid rgba(99,102,241,.28)" : "1px solid #e5eaf2",')
seg = seg.replace('border: "1px solid #d8dcff",', 'border: darkModeEnabled ? "1px solid rgba(99,102,241,.28)" : "1px solid #d8dcff",')
seg = seg.replace('background: "#fff",', 'background: darkModeEnabled ? "rgba(12,24,49,.92)" : "#fff",')
seg = seg.replace('background: "#eef2f7",', 'background: darkModeEnabled ? "rgba(79,70,229,.24)" : "#eef2f7",')
seg = seg.replace('color: "#64748b",', 'color: darkModeEnabled ? "#c7d2fe" : "#64748b",')
seg = seg.replace('color: "var(--color-dark)",', 'color: darkModeEnabled ? "#f8fafc" : "var(--color-dark)",')
seg = seg.replace('color: "var(--color-muted)",', 'color: darkModeEnabled ? "#94a3b8" : "var(--color-muted)",')
seg = seg.replace('color: "var(--color-primary)",', 'color: darkModeEnabled ? "#c7d2fe" : "var(--color-primary)",')
s = s[:start] + seg + s[end:]

# Fix Block 02 pipeline segment directly.
start = s.find('<StepHeader number="02" title="Live execution flow" />')
end = s.find('<StepHeader number="03"', start)
if start == -1 or end == -1:
    raise SystemExit("FAILED: block 02 segment not found")

seg = s[start:end]
seg = seg.replace('border: "1px solid #e5eaf2",', 'border: darkModeEnabled ? "1px solid rgba(99,102,241,.28)" : "1px solid #e5eaf2",')
seg = seg.replace('border: "1px solid #dbeafe",', 'border: darkModeEnabled ? "1px solid rgba(99,102,241,.28)" : "1px solid #dbeafe",')
seg = seg.replace('background: "#fff",', 'background: darkModeEnabled ? "rgba(12,24,49,.92)" : "#fff",')
seg = seg.replace('background: "#ffffff",', 'background: darkModeEnabled ? "rgba(12,24,49,.92)" : "#ffffff",')
seg = seg.replace('background: "linear-gradient(135deg,#eff6ff,#ffffff)",', 'background: darkModeEnabled ? "rgba(12,24,49,.92)" : "linear-gradient(135deg,#eff6ff,#ffffff)",')
seg = seg.replace('color: "var(--color-dark)",', 'color: darkModeEnabled ? "#f8fafc" : "var(--color-dark)",')
seg = seg.replace('color: "var(--color-muted)",', 'color: darkModeEnabled ? "#94a3b8" : "var(--color-muted)",')
seg = seg.replace('color: "var(--color-brand)",', 'color: darkModeEnabled ? "#c7d2fe" : "var(--color-brand)",')
s = s[:start] + seg + s[end:]

TARGET.write_text(s, encoding="utf-8")

print("CURRENT_EXACT_INTEGRATION_BLOCK2_DARK_FIXED")
print(f"Backup: {backup}")