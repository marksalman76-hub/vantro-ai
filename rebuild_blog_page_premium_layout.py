from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
BLOG_PAGE = ROOT / "frontend" / "src" / "app" / "blog" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"blog_page_before_premium_rebuild_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(BLOG_PAGE, backup)

BLOG_PAGE.write_text(r'''"use client";

import Link from "next/link";

const featured = {
  title: "How governed AI agents change ecommerce operations",
  category: "AI Operations",
  read: "7 min read",
  date: "25 May 2026",
  summary:
    "A practical guide to using specialist AI agents for product research, UGC, ads, SEO, CRM and support while keeping approval controls in place.",
};

const posts = [
  ["AI Strategy", "Why generic AI content is not enough for ecommerce brands", "Premium ecommerce output needs product context, offer positioning, audience awareness, buyer intent and conversion discipline.", "5 min read"],
  ["Automation", "What governed automation means for online stores", "How approval-safe AI workflows help teams move faster without handing over risky business decisions.", "6 min read"],
  ["UGC & Creative", "Building better UGC prompts for ecommerce campaigns", "A breakdown of hooks, creator direction, product proof, objections and conversion-focused story structure.", "4 min read"],
  ["White-label", "The future of white-label AI workforce platforms", "How agencies and operators can package specialist AI agents into scalable client-ready systems.", "8 min read"],
  ["SEO", "How AI agents can improve ecommerce SEO workflows", "From keyword mapping to product metadata, collection strategy and content briefs.", "5 min read"],
  ["Growth", "Using AI agents to find product and market opportunities", "How ecommerce teams can identify gaps, angles, competitors and buyer intent faster.", "6 min read"],
];

export default function BlogPage() {
  return (
    <main className="blogPage">
      <nav className="blogNav">
        <Link href="/" className="brand">
          <span>◈</span>
          <strong>NEXUS AI</strong>
        </Link>
        <div>
          <Link href="/">Home</Link>
          <Link href="/about">About</Link>
          <Link href="/support-request">Contact</Link>
        </div>
      </nav>

      <section className="blogHero">
        <div className="eyebrow">NEXUS AI JOURNAL</div>
        <h1>Ideas for building, selling and operating AI workforces.</h1>
        <p>
          Practical insights on ecommerce automation, AI agents, governed execution,
          premium content systems, white-label delivery and scalable digital operations.
        </p>
      </section>

      <section className="featuredGrid">
        <article className="featuredPost">
          <div className="postMeta">
            <span>{featured.category}</span>
            <span>{featured.read}</span>
            <span>{featured.date}</span>
          </div>
          <h2>{featured.title}</h2>
          <p>{featured.summary}</p>
          <button type="button">Read featured article</button>
        </article>

        <aside className="editorCard">
          <div className="editorGlow" />
          <div className="editorLabel">Editor&apos;s note</div>
          <h3>AI content is only valuable when it becomes business execution.</h3>
          <p>
            The best ecommerce systems combine creative output, operational workflow,
            governance, analytics and client-specific context.
          </p>
        </aside>
      </section>

      <section className="topicStrip">
        {["AI Agents", "UGC", "SEO", "Automation", "Ecommerce", "White-label", "Growth"].map((topic) => (
          <span key={topic}>{topic}</span>
        ))}
      </section>

      <section className="postGrid">
        {posts.map(([category, title, summary, read]) => (
          <article className="postCard" key={title}>
            <div className="postCategory">{category}</div>
            <h2>{title}</h2>
            <p>{summary}</p>
            <div className="postFooter">
              <span>{read}</span>
              <button type="button">Read article →</button>
            </div>
          </article>
        ))}
      </section>

      <section className="newsletter">
        <div>
          <span>Stay ahead</span>
          <h2>Get practical AI workforce insights.</h2>
          <p>New guides on ecommerce automation, agent systems and governed execution.</p>
        </div>
        <Link href="/support-request">Contact us</Link>
      </section>

      <footer className="blogFooter">
        <span>© 2026 Nexus AI</span>
        <div>
          <Link href="/privacy-policy">Privacy</Link>
          <Link href="/terms-of-service">Terms</Link>
          <Link href="/cookies">Cookies</Link>
        </div>
      </footer>

      <style jsx>{`
        .blogPage {
          min-height: 100vh;
          background:
            radial-gradient(circle at 18% 0%, rgba(124,58,237,.28), transparent 32%),
            radial-gradient(circle at 86% 8%, rgba(14,207,188,.16), transparent 30%),
            #05070d;
          color: #f8fafc;
          font-family: Inter, ui-sans-serif, system-ui;
        }

        .blogNav {
          position: sticky;
          top: 0;
          z-index: 20;
          height: 76px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 7vw;
          background: rgba(5,7,13,.82);
          backdrop-filter: blur(20px);
          border-bottom: 1px solid rgba(255,255,255,.08);
        }

        .brand,
        .blogNav a {
          color: #f8fafc;
          text-decoration: none;
          font-weight: 900;
        }

        .brand {
          display: flex;
          align-items: center;
          gap: 10px;
          letter-spacing: .08em;
        }

        .brand span {
          color: #8b5cf6;
        }

        .blogNav div {
          display: flex;
          gap: 24px;
        }

        .blogNav div a {
          color: #aab3c5;
          font-size: 14px;
        }

        .blogHero {
          max-width: 1120px;
          margin: 0 auto;
          padding: 110px 24px 52px;
        }

        .eyebrow,
        .editorLabel,
        .newsletter span {
          color: #c4ff00;
          font-size: 12px;
          font-weight: 950;
          letter-spacing: .16em;
          text-transform: uppercase;
        }

        .blogHero h1 {
          max-width: 980px;
          margin: 18px 0 22px;
          font-size: clamp(52px, 8vw, 108px);
          line-height: .9;
          letter-spacing: -.075em;
          background: linear-gradient(135deg, #fff, #a5b4fc, #5eead4);
          -webkit-background-clip: text;
          background-clip: text;
          color: transparent;
        }

        .blogHero p {
          max-width: 740px;
          color: #aab3c5;
          font-size: 19px;
          line-height: 1.7;
        }

        .featuredGrid,
        .postGrid,
        .newsletter {
          max-width: 1120px;
          margin: 0 auto;
          padding: 0 24px;
        }

        .featuredGrid {
          display: grid;
          grid-template-columns: 1.45fr .85fr;
          gap: 20px;
          margin-bottom: 34px;
        }

        .featuredPost,
        .editorCard,
        .postCard,
        .newsletter {
          border: 1px solid rgba(165,180,252,.16);
          background: linear-gradient(180deg, rgba(255,255,255,.075), rgba(255,255,255,.03));
          box-shadow: 0 28px 90px rgba(0,0,0,.32), inset 0 1px 0 rgba(255,255,255,.08);
          backdrop-filter: blur(18px);
        }

        .featuredPost {
          border-radius: 34px;
          padding: clamp(28px, 4vw, 46px);
          min-height: 380px;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
        }

        .postMeta {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
        }

        .postMeta span,
        .topicStrip span {
          border: 1px solid rgba(196,255,0,.18);
          background: rgba(196,255,0,.08);
          color: #d9ff70;
          padding: 9px 12px;
          border-radius: 999px;
          font-size: 12px;
          font-weight: 900;
        }

        .featuredPost h2 {
          margin: 36px 0 14px;
          font-size: clamp(34px, 5vw, 62px);
          line-height: .98;
          letter-spacing: -.055em;
        }

        .featuredPost p,
        .editorCard p,
        .postCard p,
        .newsletter p {
          color: #aab3c5;
          line-height: 1.7;
        }

        .featuredPost button,
        .postFooter button,
        .newsletter a {
          border: 0;
          color: #05070d;
          background: #c4ff00;
          border-radius: 16px;
          padding: 14px 18px;
          font-weight: 950;
          cursor: pointer;
          text-decoration: none;
        }

        .editorCard {
          position: relative;
          overflow: hidden;
          border-radius: 34px;
          padding: 30px;
        }

        .editorGlow {
          position: absolute;
          inset: -30% -30% auto auto;
          width: 260px;
          height: 260px;
          border-radius: 999px;
          background: radial-gradient(circle, rgba(124,58,237,.42), transparent 70%);
          filter: blur(14px);
        }

        .editorCard h3 {
          position: relative;
          font-size: 30px;
          line-height: 1.05;
          letter-spacing: -.04em;
        }

        .editorCard p,
        .editorLabel {
          position: relative;
        }

        .topicStrip {
          max-width: 1120px;
          margin: 0 auto 34px;
          padding: 0 24px;
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
        }

        .postGrid {
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: 18px;
          padding-bottom: 52px;
        }

        .postCard {
          border-radius: 28px;
          padding: 24px;
          min-height: 290px;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          transition: transform .25s ease, border-color .25s ease;
        }

        .postCard:hover {
          transform: translateY(-6px);
          border-color: rgba(196,255,0,.32);
        }

        .postCategory {
          color: #5eead4;
          font-size: 12px;
          font-weight: 950;
          letter-spacing: .12em;
          text-transform: uppercase;
        }

        .postCard h2 {
          margin: 18px 0 10px;
          font-size: 25px;
          line-height: 1.08;
          letter-spacing: -.04em;
        }

        .postFooter {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 12px;
          margin-top: 22px;
          color: #94a3b8;
          font-size: 13px;
          font-weight: 800;
        }

        .postFooter button {
          padding: 10px 12px;
          background: rgba(255,255,255,.08);
          color: #f8fafc;
          border: 1px solid rgba(255,255,255,.12);
        }

        .newsletter {
          border-radius: 34px;
          padding: 34px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 20px;
          margin-bottom: 56px;
        }

        .newsletter h2 {
          margin: 12px 0 8px;
          font-size: clamp(30px, 4vw, 48px);
          line-height: .98;
          letter-spacing: -.05em;
        }

        .blogFooter {
          max-width: 1120px;
          margin: 0 auto;
          padding: 26px 24px 38px;
          display: flex;
          justify-content: space-between;
          color: #64748b;
          border-top: 1px solid rgba(255,255,255,.08);
        }

        .blogFooter a {
          color: #94a3b8;
          text-decoration: none;
          margin-left: 18px;
          font-weight: 800;
        }

        @media (max-width: 900px) {
          .featuredGrid,
          .postGrid {
            grid-template-columns: 1fr;
          }

          .newsletter {
            align-items: flex-start;
            flex-direction: column;
          }

          .blogNav div {
            display: none;
          }
        }
      `}</style>
    </main>
  );
}
''', encoding="utf-8")

print("BLOG_PAGE_PREMIUM_LAYOUT_REBUILT")
print(f"Backup: {backup}")