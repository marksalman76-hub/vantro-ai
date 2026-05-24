from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"client_page_before_block2_pipeline_direct_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")

# 1) Directly darken integration pill button surfaces inside the integrations strip only.
start = s.find('className="client-integrations-strip"')
end = s.find('className="client-run-flow-grid"', start)

if start == -1 or end == -1:
    raise SystemExit("FAILED: integration/run-flow markers not found")

integration_segment = s[start:end]

integration_segment = integration_segment.replace(
    'background: "#fff",',
    'background: darkModeEnabled ? "rgba(12,24,49,.92)" : "#fff",'
)
integration_segment = integration_segment.replace(
    'background: "#eef2f7",',
    'background: darkModeEnabled ? "rgba(79,70,229,.24)" : "#eef2f7",'
)
integration_segment = integration_segment.replace(
    'border: "1px solid #e5eaf2",',
    'border: darkModeEnabled ? "1px solid rgba(99,102,241,.28)" : "1px solid #e5eaf2",'
)
integration_segment = integration_segment.replace(
    'border: "1px solid #d8dcff",',
    'border: darkModeEnabled ? "1px solid rgba(99,102,241,.28)" : "1px solid #d8dcff",'
)
integration_segment = integration_segment.replace(
    'color: "#64748b",',
    'color: darkModeEnabled ? "#c7d2fe" : "#64748b",'
)
integration_segment = integration_segment.replace(
    'color: "var(--color-dark)",',
    'color: darkModeEnabled ? "#f8fafc" : "var(--color-dark)",'
)
integration_segment = integration_segment.replace(
    'color: "var(--color-muted)",',
    'color: darkModeEnabled ? "#94a3b8" : "var(--color-muted)",'
)
integration_segment = integration_segment.replace(
    'color: "var(--color-primary)",',
    'color: darkModeEnabled ? "#c7d2fe" : "var(--color-primary)",'
)

s = s[:start] + integration_segment + s[end:]


# 2) Directly darken Block 02 pipeline rows only.
start = s.find('StepHeader number="02"')
end = s.find('StepHeader number="03"', start)

if start == -1 or end == -1:
    raise SystemExit("FAILED: block 02/03 markers not found")

block2_segment = s[start:end]

block2_segment = block2_segment.replace(
    'background: "#fff",',
    'background: darkModeEnabled ? "rgba(12,24,49,.92)" : "#fff",'
)
block2_segment = block2_segment.replace(
    'background: "#ffffff",',
    'background: darkModeEnabled ? "rgba(12,24,49,.92)" : "#ffffff",'
)
block2_segment = block2_segment.replace(
    'background: "linear-gradient(135deg,#eff6ff,#ffffff)",',
    'background: darkModeEnabled ? "rgba(12,24,49,.92)" : "linear-gradient(135deg,#eff6ff,#ffffff)",'
)
block2_segment = block2_segment.replace(
    'border: "1px solid #e5eaf2",',
    'border: darkModeEnabled ? "1px solid rgba(99,102,241,.28)" : "1px solid #e5eaf2",'
)
block2_segment = block2_segment.replace(
    'border: "1px solid #dbeafe",',
    'border: darkModeEnabled ? "1px solid rgba(99,102,241,.28)" : "1px solid #dbeafe",'
)
block2_segment = block2_segment.replace(
    'color: "var(--color-dark)",',
    'color: darkModeEnabled ? "#f8fafc" : "var(--color-dark)",'
)
block2_segment = block2_segment.replace(
    'color: "var(--color-muted)",',
    'color: darkModeEnabled ? "#94a3b8" : "var(--color-muted)",'
)
block2_segment = block2_segment.replace(
    'color: "var(--color-brand)",',
    'color: darkModeEnabled ? "#c7d2fe" : "var(--color-brand)",'
)

s = s[:start] + block2_segment + s[end:]

TARGET.write_text(s, encoding="utf-8")

print("BLOCK2_PIPELINE_AND_INTEGRATION_DIRECT_FIXED")
print(f"Backup: {backup}")