from pathlib import Path
from datetime import datetime

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "client" / "page.tsx"
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"client_page_before_dark_bottom_inner_cards_{timestamp}.tsx"

s = target.read_text(encoding="utf-8")
backup.write_text(s, encoding="utf-8")

marker = "BOTTOM_DARK_INNER_CARD_POLISH_V1"

if marker in s:
    raise SystemExit("Bottom dark inner card polish already installed.")

main_pos = s.find("<main")
if main_pos == -1:
    raise SystemExit("Could not find <main>.")

main_open_end = s.find(">", main_pos)
if main_open_end == -1:
    raise SystemExit("Could not find <main> opening end.")

css = r'''
        {/* BOTTOM_DARK_INNER_CARD_POLISH_V1 */}
        <style>{`
          ${darkModeEnabled ? `
            main section:nth-of-type(n+4) div[style*="background: #fff"],
            main section:nth-of-type(n+4) div[style*='background: "#fff"'],
            main section:nth-of-type(n+4) button[style*="background: #fff"],
            main section:nth-of-type(n+4) button[style*='background: "#fff"'] {
              background: rgba(12, 24, 49, .92) !important;
              border-color: rgba(99,102,241,.24) !important;
              color: #f8fafc !important;
              box-shadow: 0 14px 40px rgba(0,0,0,.24) !important;
            }

            main section:nth-of-type(n+4) div[style*="Generated"],
            main section:nth-of-type(n+4) div[style*="Reviewed"],
            main section:nth-of-type(n+4) div[style*="Approved"],
            main section:nth-of-type(n+4) div[style*="Pending"] {
              color: #f8fafc !important;
            }

            main section:nth-of-type(n+4) [style*="No asset generated yet"],
            main section:nth-of-type(n+4) [style*="Media preview"] {
              color: #f8fafc !important;
            }

            main section:nth-of-type(n+4) [style*="border: 1px solid #e5eaf2"],
            main section:nth-of-type(n+4) [style*='border: "1px solid #e5eaf2"'] {
              border-color: rgba(99,102,241,.24) !important;
            }

            main section:nth-of-type(n+4) input,
            main section:nth-of-type(n+4) textarea {
              background: rgba(3, 10, 24, .86) !important;
              color: #f8fafc !important;
              border-color: rgba(129,140,248,.34) !important;
            }

            main section:nth-of-type(n+4) p,
            main section:nth-of-type(n+4) span,
            main section:nth-of-type(n+4) div {
              color: inherit;
            }

            main section:nth-of-type(n+4) [style*="color: #0f172a"],
            main section:nth-of-type(n+4) [style*="color: var(--color-dark)"] {
              color: #f8fafc !important;
            }

            main section:nth-of-type(n+4) [style*="color: #334155"],
            main section:nth-of-type(n+4) [style*="color: #475569"],
            main section:nth-of-type(n+4) [style*="color: #64748b"],
            main section:nth-of-type(n+4) [style*="color: var(--color-muted)"] {
              color: #94a3b8 !important;
            }

            main section:nth-of-type(n+4) [style*="background: rgba(248,250,252"],
            main section:nth-of-type(n+4) [style*="background: #f8fafc"],
            main section:nth-of-type(n+4) [style*='background: "#f8fafc"'] {
              background: rgba(15,23,42,.86) !important;
            }
          ` : ``}
        `}</style>
'''

s = s[:main_open_end + 1] + "\n" + css + s[main_open_end + 1:]

target.write_text(s, encoding="utf-8")

print("DARK_MODE_BOTTOM_INNER_CARDS_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {target}")