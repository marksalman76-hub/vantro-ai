from pathlib import Path
from datetime import datetime
import shutil

TARGET = Path("frontend/src/app/page.tsx")
content = TARGET.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup_file = backup_dir / f"homepage_before_global_ux_rebalance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup_file)

copy_replacements = {
    "Premium AI workforce platform for ecommerce operators":
    "Premium AI workforce platform",

    "Run your ecommerce business with a governed AI workforce.\n          <br />\n          Create, execute, support and optimise at scale":
    "AI agents that plan, create and execute.\n          <br />\n          With governance built in.",

    "with specialised AI agents for ecommerce growth, content, support, analytics and governed execution.":
    "with modular AI agents for operations, growth, support, content, analytics and live business execution.",

    "Built for <strong>serious ecommerce teams</strong> that need premium execution, not generic AI output":
    "Built for <strong>serious teams</strong> that need premium execution, not generic AI output",

    "Your ecommerce<br />AI workforce.":
    "Your modular<br />AI workforce.",

    "Specialised agents for content, support, analytics, product growth and governed live execution.":
    "Specialised agents for operations, content, growth, support, analytics and governed execution.",

    "Premium ecommerce content generation.":
    "Premium business output generation.",

    "UGC, product creatives, ads, landing pages and campaign assets generated through governed AI workflows.":
    "Creative assets, workflows, support responses, analysis and execution plans generated through governed AI workflows.",

    "Built for serious ecommerce operators.":
    "Built for serious operators.",

    "Launch a premium AI workforce<br />for your ecommerce business.":
    "Launch a premium AI workforce<br />for your business.",

    "Premium ecommerce outputs · Governed live execution · Owner-controlled growth":
    "Premium outputs · Governed live execution · Owner-controlled growth",
}

for old, new in copy_replacements.items():
    if old not in content:
        print("COPY WARNING missing:", old[:90])
    content = content.replace(old, new)

rebalance_css = r'''

  /* ── GLOBAL HOMEPAGE UX REBALANCE ── */
  .nav {
    height: 66px;
  }

  .nav__inner {
    padding: 0 28px;
  }

  .nav__logo {
    transform: scale(0.92);
    transform-origin: left center;
  }

  .nav__links {
    gap: 18px;
  }

  .nav__link,
  .nav__btn-secondary,
  .nav__btn-primary {
    font-size: 12.5px;
  }

  .hero {
    min-height: 82vh;
    padding-top: 28px;
  }

  .hero__content {
    max-width: 1040px;
    padding-top: 0;
  }

  .hero__badge {
    transform: scale(0.9);
    margin-bottom: 18px;
  }

  .hero__headline {
    max-width: 900px;
    font-size: clamp(42px, 6.2vw, 82px);
    line-height: 0.96;
    letter-spacing: -0.062em;
  }

  .hero__subline {
    max-width: 720px;
    margin-top: 20px;
    font-size: clamp(16px, 1.45vw, 20px);
    line-height: 1.55;
  }

  .hero__cta-row {
    margin-top: 28px;
  }

  .hero__cta-primary,
  .hero__cta-secondary {
    min-height: 44px;
    padding: 0 18px;
    font-size: 13.5px;
    border-radius: 14px;
  }

  .hero__trust {
    margin-top: 26px;
    transform: scale(0.92);
  }

  .section-header {
    margin-bottom: 42px;
  }

  .section-eyebrow {
    font-size: 11px;
    padding: 7px 10px;
  }

  .section-title {
    font-size: clamp(34px, 4.6vw, 58px);
    line-height: 1.02;
    letter-spacing: -0.055em;
  }

  .section-subtitle {
    max-width: 680px;
    font-size: 15.5px;
    line-height: 1.62;
  }

  .stats-strip {
    padding: 30px 24px;
    gap: 18px;
  }

  .stats-strip__item {
    padding: 18px 14px;
  }

  .stats-strip__value {
    font-size: clamp(26px, 3vw, 38px);
  }

  .stats-strip__label {
    font-size: 12px;
  }

  .agents,
  .bento,
  .pricing,
  .testimonials,
  .final-cta {
    padding-top: 86px;
    padding-bottom: 86px;
  }

  .agents__grid {
    gap: 16px;
  }

  .agent-card {
    min-height: 176px;
    padding: 18px;
    border-radius: 22px;
  }

  .agent-card__icon-wrap {
    width: 44px;
    height: 44px;
    border-radius: 14px;
  }

  .agent-card__name {
    font-size: 15px;
  }

  .agent-card__role,
  .agent-card__specialty {
    font-size: 12px;
    line-height: 1.45;
  }

  .agent-card__stat,
  .agent-card__status {
    font-size: 10.5px;
  }

  .bento__grid {
    gap: 18px;
  }

  .bento-card {
    padding: 24px;
    border-radius: 24px;
  }

  .bento-card--xl {
    min-height: 360px;
  }

  .bento-card--md {
    min-height: 260px;
  }

  .bento-card--sm {
    min-height: 190px;
  }

  .bento-card__eyebrow {
    font-size: 11px;
  }

  .bento-card__title {
    font-size: clamp(23px, 2.4vw, 34px);
    line-height: 1.08;
  }

  .bento-card__body {
    font-size: 13.5px;
    line-height: 1.62;
  }

  .pricing__grid {
    gap: 18px;
  }

  .pricing-card {
    padding: 24px;
    border-radius: 24px;
  }

  .pricing-card__name {
    font-size: 17px;
  }

  .pricing-card__price {
    font-size: 42px;
  }

  .pricing-card__desc,
  .pricing-card__features li {
    font-size: 13px;
    line-height: 1.55;
  }

  .pricing-card__cta {
    min-height: 42px;
    font-size: 13px;
    border-radius: 13px;
  }

  .testimonial-card {
    width: 340px;
    padding: 22px;
    border-radius: 22px;
  }

  .testimonial-card__text {
    font-size: 13.5px;
    line-height: 1.62;
  }

  .final-cta__inner {
    padding: 62px 34px;
    border-radius: 30px;
  }

  .final-cta__title {
    font-size: clamp(36px, 5vw, 66px);
    line-height: 1;
    letter-spacing: -0.055em;
  }

  .final-cta__sub {
    font-size: 15px;
    line-height: 1.6;
  }

  .footer {
    padding-top: 56px;
  }

  @media (max-width: 820px) {
    .hero {
      min-height: 78vh;
    }

    .hero__headline {
      font-size: clamp(40px, 13vw, 64px);
    }

    .agents,
    .bento,
    .pricing,
    .testimonials,
    .final-cta {
      padding-top: 64px;
      padding-bottom: 64px;
    }

    .section-title {
      font-size: clamp(32px, 10vw, 48px);
    }
  }
'''

if "/* ── GLOBAL HOMEPAGE UX REBALANCE ── */" not in content:
    end_marker = "\n`;\n"
    if end_marker not in content:
        raise RuntimeError("Could not find CSS constant closing marker.")
    content = content.replace(end_marker, rebalance_css + end_marker, 1)

TARGET.write_text(content, encoding="utf-8")

print("HOMEPAGE_GLOBAL_UX_REBALANCED")
print("Backup:", backup_file)