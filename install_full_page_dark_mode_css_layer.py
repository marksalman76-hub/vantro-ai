from pathlib import Path
from datetime import datetime

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "client" / "page.tsx"
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"client_page_before_full_page_dark_css_layer_{timestamp}.tsx"

s = target.read_text(encoding="utf-8")
backup.write_text(s, encoding="utf-8")

marker = "FULL_PAGE_DARK_MODE_CSS_LAYER_V1"

if marker in s:
    raise SystemExit("Dark mode CSS layer already installed.")

main_pos = s.find("<main")
if main_pos == -1:
    raise SystemExit("Could not find <main> tag.")

main_open_end = s.find(">", main_pos)
if main_open_end == -1:
    raise SystemExit("Could not find <main> opening end.")

css_layer = r'''
        {/* FULL_PAGE_DARK_MODE_CSS_LAYER_V1 */}
        <style>{`
          ${darkModeEnabled ? `
            html,
            body {
              background: #050b18 !important;
            }

            main {
              background:
                radial-gradient(circle at 18% 0%, rgba(79,70,229,.20), transparent 28%),
                radial-gradient(circle at 92% 6%, rgba(124,58,237,.16), transparent 30%),
                linear-gradient(180deg, #050b18 0%, #071120 48%, #050b18 100%) !important;
              color: #f8fafc !important;
            }

            main section,
            main article,
            main aside {
              background: linear-gradient(180deg, rgba(10,22,46,.96), rgba(7,16,34,.98)) !important;
              border-color: rgba(99,102,241,.24) !important;
              box-shadow: 0 24px 80px rgba(0,0,0,.34) !important;
              color: #f8fafc !important;
            }

            main div[style*="background: #fff"],
            main div[style*='background: "#fff"'],
            main div[style*="background:#fff"],
            main button[style*="background: #fff"],
            main button[style*='background: "#fff"'],
            main button[style*="background:#fff"] {
              background: rgba(12, 24, 49, .92) !important;
              border-color: rgba(99,102,241,.24) !important;
              color: #f8fafc !important;
              box-shadow: 0 14px 44px rgba(0,0,0,.24) !important;
            }

            main div[style*="rgba(238,242,255"],
            main button[style*="rgba(238,242,255"],
            main span[style*="rgba(238,242,255"] {
              background: rgba(79,70,229,.18) !important;
              border-color: rgba(129,140,248,.30) !important;
              color: #dbeafe !important;
            }

            main input,
            main textarea,
            main select {
              background: rgba(3, 10, 24, .86) !important;
              color: #f8fafc !important;
              border-color: rgba(129,140,248,.34) !important;
              box-shadow: inset 0 0 0 1px rgba(255,255,255,.02) !important;
            }

            main input::placeholder,
            main textarea::placeholder {
              color: rgba(203,213,225,.72) !important;
            }

            main h1,
            main h2,
            main h3,
            main h4,
            main strong {
              color: #ffffff !important;
            }

            main p,
            main label,
            main small,
            main span,
            main div {
              color: inherit;
            }

            main [style*="color: var(--color-dark)"],
            main [style*="color: #0f172a"],
            main [style*="color: #334155"] {
              color: #f8fafc !important;
            }

            main [style*="color: var(--color-muted)"],
            main [style*="color: #64748b"],
            main [style*="color: #475569"] {
              color: #94a3b8 !important;
            }

            main [style*="color: var(--color-brand)"],
            main [style*="color: #4f46e5"] {
              color: #a5b4fc !important;
            }

            main button {
              border-color: rgba(129,140,248,.28) !important;
            }

            main button:hover {
              filter: brightness(1.08);
            }

            main [style*="linear-gradient(135deg,#4f46e5,#4338ca)"],
            main [style*="linear-gradient(135deg, #4f46e5, #4338ca)"] {
              background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
              color: #ffffff !important;
              box-shadow: 0 14px 38px rgba(79,70,229,.32) !important;
            }

            main div[style*="borderLeft"],
            main div[style*="border-left"] {
              border-color: rgba(129,140,248,.26) !important;
            }

            #media-preview-popup,
            #media-preview-popup * {
              color: #0f172a;
            }
          ` : ``}
        `}</style>
'''

s = s[:main_open_end + 1] + "\n" + css_layer + s[main_open_end + 1:]

target.write_text(s, encoding="utf-8")

print("FULL_PAGE_DARK_MODE_CSS_LAYER_INSTALLED")
print(f"Backup: {backup}")
print(f"Updated: {target}")