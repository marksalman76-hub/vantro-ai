from pathlib import Path
from datetime import datetime

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "client" / "page.tsx"
backup_dir = root / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = backup_dir / f"client_page_before_bottom_section_dark_consistency_{timestamp}.tsx"

s = target.read_text(encoding="utf-8")
backup.write_text(s, encoding="utf-8")

section_old = '<section style={{ ...responsiveSecondaryGridStyle, alignItems: "stretch" }}>'
section_new = '<section className="client-bottom-workspace" style={{ ...responsiveSecondaryGridStyle, alignItems: "stretch" }}>'

if section_new not in s:
    if section_old not in s:
        raise SystemExit("Bottom section opening tag not found.")
    s = s.replace(section_old, section_new, 1)

marker = "BOTTOM_SECTION_DARK_CONSISTENCY_V1"

if marker in s:
    raise SystemExit("Bottom section dark consistency CSS already installed.")

main_pos = s.find("<main")
if main_pos == -1:
    raise SystemExit("Could not find <main>.")

main_open_end = s.find(">", main_pos)
if main_open_end == -1:
    raise SystemExit("Could not find <main> opening end.")

css = r'''
        {/* BOTTOM_SECTION_DARK_CONSISTENCY_V1 */}
        <style>{`
          ${darkModeEnabled ? `
            .client-bottom-workspace,
            .client-bottom-workspace > div {
              color: #f8fafc !important;
            }

            .client-bottom-workspace > div {
              background:
                linear-gradient(180deg, rgba(10,22,46,.96), rgba(7,16,34,.98)) !important;
              border: 1px solid rgba(99,102,241,.24) !important;
              box-shadow: 0 24px 80px rgba(0,0,0,.34) !important;
            }

            .client-bottom-workspace div[style*="background: #fff"],
            .client-bottom-workspace div[style*="background: \\"#fff\\""],
            .client-bottom-workspace button[style*="background: #fff"],
            .client-bottom-workspace button[style*="background: \\"#fff\\""],
            .client-bottom-workspace span[style*="background: #fff"],
            .client-bottom-workspace span[style*="background: \\"#fff\\""] {
              background: rgba(12,24,49,.92) !important;
              border-color: rgba(99,102,241,.24) !important;
              color: #f8fafc !important;
              box-shadow: 0 12px 36px rgba(0,0,0,.22) !important;
            }

            .client-bottom-workspace div[style*="linear-gradient(180deg,#ffffff"],
            .client-bottom-workspace div[style*="linear-gradient(180deg, #ffffff"],
            .client-bottom-workspace div[style*="linear-gradient(180deg,#fff"],
            .client-bottom-workspace div[style*="linear-gradient(135deg,var(--color-bg-light)"] {
              background:
                linear-gradient(180deg, rgba(15,23,42,.94), rgba(8,18,40,.96)) !important;
              border-color: rgba(99,102,241,.24) !important;
              color: #f8fafc !important;
            }

            .client-bottom-workspace div[style*="background: var(--color-bg-light)"],
            .client-bottom-workspace div[style*="background: \\"var(--color-bg-light)\\""],
            .client-bottom-workspace button[style*="background: var(--color-bg-light)"],
            .client-bottom-workspace button[style*="background: \\"var(--color-bg-light)\\""] {
              background: rgba(15,23,42,.88) !important;
              border-color: rgba(99,102,241,.22) !important;
              color: #f8fafc !important;
            }

            .client-bottom-workspace div[style*="background: #f8fafc"],
            .client-bottom-workspace span[style*="background: #f8fafc"],
            .client-bottom-workspace button[style*="background: #f8fafc"] {
              background: rgba(15,23,42,.86) !important;
              color: #cbd5e1 !important;
              border-color: rgba(99,102,241,.22) !important;
            }

            .client-bottom-workspace div[style*="background: #eef2f7"],
            .client-bottom-workspace div[style*="background: #eef2ff"],
            .client-bottom-workspace span[style*="background: #eef2ff"] {
              background: rgba(79,70,229,.16) !important;
              color: #c7d2fe !important;
            }

            .client-bottom-workspace span[style*="background: #ecfdf5"],
            .client-bottom-workspace div[style*="background: #dcfce7"],
            .client-bottom-workspace div[style*="background: #fee2e2"] {
              background: rgba(34,197,94,.14) !important;
              border-color: rgba(34,197,94,.28) !important;
            }

            .client-bottom-workspace [style*="border: 1px solid #e5eaf2"],
            .client-bottom-workspace [style*="border: \\"1px solid #e5eaf2\\""],
            .client-bottom-workspace [style*="borderTop: \\"1px solid #edf1f6\\""],
            .client-bottom-workspace [style*="border-top: 1px solid #edf1f6"] {
              border-color: rgba(99,102,241,.24) !important;
            }

            .client-bottom-workspace [style*="border: 1px dashed #dbe4ee"],
            .client-bottom-workspace [style*="border: 1px dashed #cbd5e1"] {
              border-color: rgba(148,163,184,.32) !important;
            }

            .client-bottom-workspace h3,
            .client-bottom-workspace h4,
            .client-bottom-workspace [style*="color: var(--color-dark)"],
            .client-bottom-workspace [style*="color: #0f172a"] {
              color: #f8fafc !important;
            }

            .client-bottom-workspace [style*="color: var(--color-muted)"],
            .client-bottom-workspace [style*="color: var(--color-mid)"],
            .client-bottom-workspace [style*="color: #334155"],
            .client-bottom-workspace [style*="color: #475569"],
            .client-bottom-workspace [style*="color: #64748b"],
            .client-bottom-workspace [style*="color: #94a3b8"] {
              color: #94a3b8 !important;
            }

            .client-bottom-workspace [style*="color: var(--color-brand)"],
            .client-bottom-workspace [style*="color: #4f46e5"] {
              color: #a5b4fc !important;
            }

            .client-bottom-workspace button {
              border-color: rgba(129,140,248,.30) !important;
            }

            .client-bottom-workspace button:hover {
              filter: brightness(1.08);
            }

            .client-bottom-workspace img {
              background: rgba(15,23,42,.86) !important;
            }

            .client-bottom-workspace div[style*="height: 9"] {
              background: rgba(30,41,59,.92) !important;
            }
          ` : ``}
        `}</style>
'''

s = s[:main_open_end + 1] + "\n" + css + s[main_open_end + 1:]

target.write_text(s, encoding="utf-8")

print("BOTTOM_SECTION_DARK_CONSISTENCY_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {target}")