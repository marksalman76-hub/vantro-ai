from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"page_before_nexus_footer_links_direct_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(PAGE, backup)

s = PAGE.read_text(encoding="utf-8")

old = '''function Footer() {
  const cols = [
    { title: "Product",    links: ["Platform","Agents","Studio","API & MCP","Changelog"] },
    { title: "Company",    links: ["About","Blog","Careers","Press","Contact"] },
    { title: "Resources",  links: ["Docs","Templates","Status","Security"] },
    { title: "Legal",      links: ["Terms","Privacy","Cookies","Licenses"] },
  ];
  return (
    <footer className="footer">
      <div className="footer__inner">
        <div className="footer__brand">
          <a href="#" className="nav__logo">
            <span className="nav__logo-mark">◈</span>
            <span>NEXUS</span>
            <span className="nav__logo-tag">AI</span>
          </a>
          <p className="footer__tagline">The creative supercomputer<br />for the world&apos;s best teams.</p>
          <div className="footer__social">
            {["X","LinkedIn","YouTube","Discord"].map(s => (
              <a key={s} href="#" className="footer__social-link">{s}</a>
            ))}
          </div>
        </div>

        {cols.map(col => (
          <div key={col.title} className="footer__col">
            <div className="footer__col-title">{col.title}</div>
            {col.links.map(l => (
              <a key={l} href="#" className="footer__link">{l}</a>
            ))}
          </div>
        ))}
      </div>
      <div className="footer__bottom">
        <span>© 2026 Nexus AI Inc. All rights reserved.</span>
        <span>Made with ◈ by the Nexus team</span>
      </div>
    </footer>
  );
}'''

new = '''function Footer() {
  const cols = [
    {
      title: "Product",
      links: [
        ["Platform", "#platform"],
        ["Agents", "#agents"],
        ["Studio", "#studio"],
        ["API & MCP", "#api"],
        ["Changelog", "#changelog"],
      ],
    },
    {
      title: "Company",
      links: [
        ["About", "#about"],
        ["Blog", "#blog"],
        ["Careers", "/support-request"],
        ["Press", "/support-request"],
        ["Contact", "/support-request"],
      ],
    },
    {
      title: "Resources",
      links: [
        ["Docs", "#docs"],
        ["Templates", "#templates"],
        ["Status", "#status"],
        ["Security", "#security"],
      ],
    },
    {
      title: "Legal",
      links: [
        ["Terms", "/terms-of-service"],
        ["Privacy", "/privacy-policy"],
        ["Cookies", "/privacy-policy"],
        ["Licenses", "/terms-of-service"],
      ],
    },
  ];

  const socialLinks = [
    ["X", "https://x.com"],
    ["LinkedIn", "https://www.linkedin.com"],
    ["YouTube", "https://www.youtube.com"],
    ["Discord", "/support-request"],
  ];

  return (
    <footer className="footer">
      <div id="platform" className="footerAnchor" />
      <div id="api" className="footerAnchor" />
      <div id="changelog" className="footerAnchor" />
      <div id="about" className="footerAnchor" />
      <div id="blog" className="footerAnchor" />
      <div id="docs" className="footerAnchor" />
      <div id="templates" className="footerAnchor" />
      <div id="status" className="footerAnchor" />
      <div id="security" className="footerAnchor" />

      <div className="footer__inner">
        <div className="footer__brand">
          <a href="#" className="nav__logo">
            <span className="nav__logo-mark">◈</span>
            <span>NEXUS</span>
            <span className="nav__logo-tag">AI</span>
          </a>
          <p className="footer__tagline">The creative supercomputer<br />for the world&apos;s best teams.</p>
          <div className="footer__social">
            {socialLinks.map(([label, href]) => (
              <a
                key={label}
                href={href}
                target={href.startsWith("http") ? "_blank" : undefined}
                rel={href.startsWith("http") ? "noreferrer" : undefined}
                className="footer__social-link"
              >
                {label}
              </a>
            ))}
          </div>
        </div>

        {cols.map((col) => (
          <div key={col.title} className="footer__col">
            <div className="footer__col-title">{col.title}</div>
            {col.links.map(([label, href]) => (
              <a key={label} href={href} className="footer__link">{label}</a>
            ))}
          </div>
        ))}
      </div>
      <div className="footer__bottom">
        <span>© 2026 Nexus AI Inc. All rights reserved.</span>
        <span>Made with ◈ by the Nexus team</span>
      </div>
    </footer>
  );
}'''

if old not in s:
    raise SystemExit("FAILED: exact Footer component block not found")

s = s.replace(old, new, 1)

# Add smooth scroll and anchor offset safely inside CSS.
if ".footerAnchor" not in s:
    css_marker = "  .footer {"
    if css_marker in s:
        s = s.replace(css_marker, "  html { scroll-behavior: smooth; }\n  .footerAnchor { scroll-margin-top: 120px; }\n" + css_marker, 1)

PAGE.write_text(s, encoding="utf-8")

print("NEXUS_FOOTER_LINKS_DIRECT_FIXED")
print(f"Backup: {backup}")