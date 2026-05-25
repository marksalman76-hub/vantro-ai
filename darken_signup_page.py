from pathlib import Path
from datetime import datetime

root = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
page = root / "frontend" / "src" / "app" / "signup" / "page.tsx"
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"signup_before_dark_mode_{stamp}.tsx"

s = page.read_text(encoding="utf-8")
backup.write_text(s, encoding="utf-8")

replacements = {
    'background: "radial-gradient(circle at 12% 10%, rgba(99,91,255,.14), transparent 28%), linear-gradient(180deg,#fff 0%,#f8f9ff 100%)", fontFamily: "Inter,Arial,sans-serif", color: "#111827"':
    'background: "radial-gradient(circle at 12% 10%, rgba(99,91,255,.24), transparent 30%), radial-gradient(circle at 88% 18%, rgba(168,85,247,.16), transparent 28%), linear-gradient(180deg,#050816 0%,#0b1020 52%,#050816 100%)", fontFamily: "Inter,Arial,sans-serif", color: "#f8fafc"',

    'background: "#fff", border: "1px solid #e5e7eb"':
    'background: "rgba(15,23,42,.88)", border: "1px solid rgba(148,163,184,.18)"',

    'boxShadow: "0 24px 60px rgba(15,23,42,.06)"':
    'boxShadow: "0 28px 80px rgba(0,0,0,.38)"',

    'background: "#f8f7ff", border: "1px solid #ddd6fe"':
    'background: "rgba(99,91,255,.12)", border: "1px solid rgba(129,140,248,.28)"',

    'background: "#f8f7ff", color: "#635BFF"':
    'background: "rgba(99,91,255,.12)", color: "#c4b5fd"',

    'color: "#111827", background: "#fff"':
    'color: "#f8fafc", background: "rgba(15,23,42,.82)"',

    'border: key === planKey ? "2px solid #635BFF" : "1px solid #e5e7eb"':
    'border: key === planKey ? "2px solid #8b5cf6" : "1px solid rgba(148,163,184,.18)"',

    'boxShadow: "0 12px 32px rgba(15,23,42,.045)"':
    'boxShadow: "0 16px 42px rgba(0,0,0,.28)"',

    'background: "rgba(255,255,255,.86)", border: "1px solid #e5e7eb"':
    'background: "rgba(15,23,42,.78)", border: "1px solid rgba(148,163,184,.18)"',

    'boxShadow: "0 24px 60px rgba(15,23,42,.05)"':
    'boxShadow: "0 28px 80px rgba(0,0,0,.34)"',

    'color: category === c ? "#fff" : "#4f46e5", background: category === c ? "#635BFF" : "#eef2ff"':
    'color: category === c ? "#fff" : "#c4b5fd", background: category === c ? "linear-gradient(135deg,#635BFF,#8b5cf6)" : "rgba(99,91,255,.12)"',

    'border: isSelected ? "2px solid #635BFF" : "1px solid #e5e7eb", background: isSelected ? "#f5f3ff" : "#fff"':
    'border: isSelected ? "2px solid #8b5cf6" : "1px solid rgba(148,163,184,.18)", background: isSelected ? "rgba(99,91,255,.18)" : "rgba(15,23,42,.82)"',
}

for old, new in replacements.items():
    if old not in s:
        print("MISSING:", old[:90])
    s = s.replace(old, new)

# darken common inline text colours
s = s.replace('color: "#111827"', 'color: "#f8fafc"')
s = s.replace('color: "#374151"', 'color: "#cbd5e1"')
s = s.replace('color: "#4b5563"', 'color: "#cbd5e1"')
s = s.replace('color: "#6b7280"', 'color: "#94a3b8"')
s = s.replace('color: "#635BFF"', 'color: "#c4b5fd"')
s = s.replace('border: "1px solid #e5e7eb"', 'border: "1px solid rgba(148,163,184,.18)"')
s = s.replace('background: "#fff"', 'background: "rgba(15,23,42,.82)"')
s = s.replace('background: "#f8f7ff"', 'background: "rgba(99,91,255,.12)"')
s = s.replace('background: "#eef2ff"', 'background: "rgba(99,91,255,.12)"')

page.write_text(s, encoding="utf-8")

print("SIGNUP_DARK_MODE_APPLIED")
print("Backup:", backup)