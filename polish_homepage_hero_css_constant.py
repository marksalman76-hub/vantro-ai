from pathlib import Path
from datetime import datetime
import shutil

TARGET = Path("frontend/src/app/page.tsx")
content = TARGET.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup_file = backup_dir / f"homepage_before_hero_css_constant_polish_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup_file)

content = content.replace(
    "The world&apos;s first unified AI creation supercomputer",
    "Premium AI workforce platform for ecommerce operators"
)

content = content.replace(
    "24/7 AI workforce for any industry.\n          <br />\n          Any operation. Any scale",
    "Run your ecommerce business with a governed AI workforce.\n          <br />\n          Create, execute, support and optimise at scale"
)

content = content.replace(
    "with a fleet of specialized AI agents that never sleep.",
    "with specialised AI agents for ecommerce growth, content, support, analytics and governed execution."
)

content = content.replace(
    "Trusted by <strong>2.1M+ creators</strong> in 120 countries",
    "Built for <strong>serious ecommerce teams</strong> that need premium execution, not generic AI output"
)

content = content.replace(
    '<a href="#pricing" className="hero__cta-primary">\n            Sign up\n            <span className="hero__cta-glow" />\n          </a>',
    '<a href="/signup" className="hero__cta-primary">\n            Start building\n            <span className="hero__cta-glow" />\n          </a>\n          <a href="/demo" className="hero__cta-secondary">\n            View demo\n          </a>'
)

premium_css = r'''

  /* ── HOMEPAGE HERO PREMIUM POLISH ── */
  .hero {
    min-height: 92vh;
    background:
      radial-gradient(circle at 50% 8%, rgba(124, 58, 237, 0.32), transparent 32%),
      radial-gradient(circle at 12% 30%, rgba(79, 70, 229, 0.24), transparent 30%),
      linear-gradient(180deg, #030712 0%, #07111f 46%, #08111f 100%);
  }

  .hero__content {
    max-width: 1180px;
    padding-top: 18px;
  }

  .hero__badge {
    border-color: rgba(168, 85, 247, 0.34);
    background: rgba(15, 23, 42, 0.72);
    box-shadow: 0 18px 70px rgba(79, 70, 229, 0.2);
    backdrop-filter: blur(18px);
  }

  .hero__headline {
    max-width: 1040px;
    margin-left: auto;
    margin-right: auto;
    letter-spacing: -0.075em;
    line-height: 0.91;
    text-wrap: balance;
  }

  .hero__subline {
    max-width: 820px;
    margin-left: auto;
    margin-right: auto;
    color: rgba(226, 232, 240, 0.82);
    text-wrap: balance;
  }

  .hero__cta-row {
    gap: 14px;
  }

  .hero__cta-primary {
    min-width: 158px;
    justify-content: center;
    box-shadow:
      0 20px 70px rgba(124, 58, 237, 0.42),
      inset 0 1px 0 rgba(255,255,255,0.18);
  }

  .hero__cta-secondary {
    min-width: 142px;
    justify-content: center;
    background: rgba(15, 23, 42, 0.74);
    border: 1px solid rgba(148, 163, 184, 0.22);
    color: rgba(248, 250, 252, 0.92);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.06);
  }

  .hero__trust {
    border: 1px solid rgba(148, 163, 184, 0.16);
    background: rgba(2, 6, 23, 0.34);
    padding: 10px 14px;
    border-radius: 999px;
    backdrop-filter: blur(18px);
  }
'''

if "/* ── HOMEPAGE HERO PREMIUM POLISH ── */" not in content:
    end_marker = "\n`;\n"
    if end_marker not in content:
        raise RuntimeError("Could not find CSS constant closing marker.")
    content = content.replace(end_marker, premium_css + end_marker, 1)

TARGET.write_text(content, encoding="utf-8")

print("HOMEPAGE_HERO_CSS_CONSTANT_POLISHED")
print("Backup:", backup_file)