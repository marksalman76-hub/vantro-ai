from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
PAGE = ROOT / "frontend" / "src" / "app" / "page.tsx"
BLOG_PAGE = ROOT / "frontend" / "src" / "app" / "blog" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"page_before_blog_route_{stamp}.tsx"
shutil.copy2(PAGE, backup)

s = PAGE.read_text(encoding="utf-8")
s = s.replace('["Blog","#features"]', '["Blog","/blog"]')
s = s.replace('href="#blog"', 'href="/blog"')
s = s.replace('href="/#blog"', 'href="/blog"')
PAGE.write_text(s, encoding="utf-8")

BLOG_PAGE.parent.mkdir(parents=True, exist_ok=True)
BLOG_PAGE.write_text(r'''"use client";

import Link from "next/link";

export default function BlogPage() {
  const posts = [
    ["How governed AI agents change ecommerce operations", "A practical look at using specialist agents for product research, content, ads, SEO, CRM and support without losing control."],
    ["Why generic AI content is not enough for ecommerce brands", "Premium ecommerce outputs need market context, offer positioning, audience awareness, brand voice and conversion intent."],
    ["The future of white-label AI workforce platforms", "Agencies and operators can package specialist AI agents into scalable client-ready systems with governance, billing and access control."]
  ];

  return (
    <main style={{ minHeight: "100vh", background: "radial-gradient(circle at top, rgba(124,58,237,.24), transparent 34%), #020617", padding: "64px 24px", color: "#f8fafc", fontFamily: "Inter, ui-sans-serif, system-ui" }}>
      <section style={{ maxWidth: 960, margin: "0 auto", background: "rgba(7,16,40,.92)", border: "1px solid rgba(99,102,241,.22)", borderRadius: 28, padding: "clamp(28px,4vw,46px)", boxShadow: "0 30px 70px rgba(0,0,0,.35)" }}>
        <div style={{ fontSize: 12, fontWeight: 900, letterSpacing: ".14em", color: "#a5b4fc", marginBottom: 10 }}>BLOG</div>
        <h1 style={{ fontSize: "clamp(40px,6vw,68px)", lineHeight: 0.95, margin: "0 0 22px", fontWeight: 950 }}>Insights on ecommerce AI, automation and governed execution.</h1>
        <p style={{ color: "#cbd5e1", lineHeight: 1.75, fontSize: 17, marginBottom: 28 }}>Explore practical ideas on building, selling and operating premium AI agent systems for ecommerce businesses.</p>

        <div style={{ display: "grid", gap: 16 }}>
          {posts.map(([title, body]) => (
            <article key={title} style={{ border: "1px solid rgba(99,102,241,.22)", borderRadius: 18, padding: "22px", background: "rgba(12,24,49,.72)" }}>
              <h2 style={{ margin: "0 0 10px", fontSize: 22 }}>{title}</h2>
              <p style={{ margin: 0, color: "#cbd5e1", lineHeight: 1.7 }}>{body}</p>
            </article>
          ))}
        </div>

        <Link href="/" style={{ display: "inline-flex", marginTop: 30, borderRadius: 16, padding: "14px 18px", background: "linear-gradient(135deg,#7c3aed,#4f46e5)", color: "#fff", textDecoration: "none", fontWeight: 900 }}>
          Back to home
        </Link>
      </section>
    </main>
  );
}
''', encoding="utf-8")

print("BLOG_PAGE_CREATED_AND_FOOTER_LINKED")
print(f"Backup: {backup}")