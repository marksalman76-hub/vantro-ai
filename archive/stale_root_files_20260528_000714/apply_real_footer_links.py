from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"page_before_real_footer_links_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(PAGE, backup)

s = PAGE.read_text(encoding="utf-8")

s = s.replace(
    '{ title: "Product",    links: ["Platform","Agents","Studio","API & MCP","Changelog"] },',
    '{ title: "Product",    links: [["Platform","#platform"],["Agents","#agents"],["Studio","#studio"],["API & MCP","#features"],["Changelog","#features"]] },'
)

s = s.replace(
    '{ title: "Company",    links: ["About","Blog","Careers","Press","Contact"] },',
    '{ title: "Company",    links: [["About","#platform"],["Blog","#features"],["Careers","/support-request"],["Press","/support-request"],["Contact","/support-request"]] },'
)

s = s.replace(
    '{ title: "Resources",  links: ["Docs","Templates","Status","Security","Privacy"] },',
    '{ title: "Resources",  links: [["Docs","#workflow"],["Templates","#studio"],["Status","#features"],["Security","#features"],["Privacy","/privacy-policy"]] },'
)

s = s.replace(
    '{ title: "Legal",      links: ["Terms","Privacy","Cookies","Licenses"] },',
    '{ title: "Legal",      links: [["Terms","/terms-of-service"],["Privacy","/privacy-policy"],["Cookies","/privacy-policy"],["Licenses","/terms-of-service"]] },'
)

old_map = '''{col.links.map(l => (
              <a key={l} href="#" className="footer__link">{l}</a>
            ))}'''

new_map = '''{col.links.map(([label, href]) => (
              <a key={label} href={href} className="footer__link">{label}</a>
            ))}'''

s = s.replace(old_map, new_map)

# add real ids to existing sections
section_ids = {
    'className="agents-section"': 'id="agents" className="agents-section"',
    'className="studio-section"': 'id="studio" className="studio-section"',
    'className="workflow-section"': 'id="workflow" className="workflow-section"',
    'className="features-section"': 'id="features" className="features-section"',
}

for old, new in section_ids.items():
    if old in s and new not in s:
        s = s.replace(old, new, 1)

# add smooth scrolling
if "scroll-behavior: smooth" not in s:
    marker = "html, body {"
    if marker in s:
        s = s.replace(
            marker,
            'html { scroll-behavior: smooth; }\n\n' + marker,
            1
        )

PAGE.write_text(s, encoding="utf-8")

print("REAL_FOOTER_LINKS_APPLIED")
print(f"Backup: {backup}")