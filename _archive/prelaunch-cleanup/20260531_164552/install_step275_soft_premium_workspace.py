from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "client" / "page.tsx"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
text = PAGE.read_text(encoding="utf-8")

backup = BACKUPS / f"client_page_before_step275_soft_workspace_{timestamp}.tsx"
backup.write_text(text, encoding="utf-8")

text = text.replace(
'''const cardStyle = {
  background: "rgba(15,23,42,.66)",
  border: "1px solid rgba(148,163,184,.16)",
  borderRadius: 24,
  boxShadow: "0 20px 60px rgba(0,0,0,.22)",
  backdropFilter: "blur(14px)",
};''',
'''const cardStyle = {
  background: "linear-gradient(135deg,rgba(15,23,42,.56),rgba(15,23,42,.34))",
  border: "1px solid rgba(148,163,184,.08)",
  borderRadius: 26,
  boxShadow: "0 24px 70px rgba(0,0,0,.18)",
  backdropFilter: "blur(18px)",
};'''
)

text = text.replace(
'''const inputStyle = {
  width: "100%",
  padding: 12,
  borderRadius: 15,
  border: "1px solid rgba(148,163,184,.14)",
  background: "rgba(2,6,23,.72)",
  color: "#fff",
  resize: "vertical" as const,
  fontSize: 13,
  lineHeight: 1.45,
  outline: "none",
};''',
'''const inputStyle = {
  width: "100%",
  padding: 12,
  borderRadius: 16,
  border: "1px solid rgba(148,163,184,.07)",
  background: "rgba(2,6,23,.48)",
  color: "#fff",
  resize: "vertical" as const,
  fontSize: 13,
  lineHeight: 1.45,
  outline: "none",
};'''
)

replacements = {
    'border: "1px solid rgba(148,163,184,.14)",': 'border: "1px solid rgba(148,163,184,.07)",',
    'background: "rgba(15,23,42,.48)",': 'background: "rgba(15,23,42,.34)",',
    'borderRadius: 999,': 'borderRadius: 24,',
    'border: "1px solid rgba(148,163,184,.18)",': 'border: "1px solid rgba(148,163,184,.08)",',
    'background: "#020617",': 'background: "rgba(2,6,23,.52)",',
    'border: "1px dashed rgba(148,163,184,.20)",': 'border: "1px dashed rgba(148,163,184,.10)",',
    'background: "linear-gradient(135deg,rgba(2,6,23,.55),rgba(15,23,42,.35))",': 'background: "linear-gradient(135deg,rgba(2,6,23,.35),rgba(15,23,42,.20))"',
}

for old, new in replacements.items():
    text = text.replace(old, new)

PAGE.write_text(text, encoding="utf-8")

print("STEP_275_SOFT_PREMIUM_WORKSPACE_INSTALLED")
print(f"Backup: {backup}")
print("STEP_275_OK")