from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"landing_page_before_hero_visual_density_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")

css = r'''
        /* LANDING_HERO_VISUAL_DENSITY_V1 */
        .heroVisualSystem{
          position:absolute;
          inset:0;
          pointer-events:none;
          overflow:hidden;
          z-index:1;
        }
        .heroGlassCard{
          position:absolute;
          width:220px;
          border-radius:24px;
          padding:16px;
          border:1px solid rgba(124,116,255,.24);
          background:linear-gradient(180deg,rgba(255,255,255,.10),rgba(255,255,255,.035));
          box-shadow:0 28px 70px rgba(0,0,0,.34), inset 0 1px 0 rgba(255,255,255,.12);
          backdrop-filter:blur(22px) saturate(150%);
          -webkit-backdrop-filter:blur(22px) saturate(150%);
          color:#fff;
          animation:heroCardFloat 7.5s ease-in-out infinite;
        }
        .heroGlassCard strong{
          display:block;
          font-size:13px;
          margin-bottom:6px;
        }
        .heroGlassCard span{
          display:block;
          color:#A7B0C6;
          font-size:12px;
          line-height:1.45;
        }
        .heroGlassCard em{
          display:inline-flex;
          margin-top:12px;
          padding:6px 9px;
          border-radius:999px;
          background:rgba(14,207,188,.13);
          color:#5EEAD4;
          font-size:11px;
          font-style:normal;
          font-weight:900;
        }
        .heroGlassCard.cardA{left:7%;top:28%;animation-delay:-.7s}
        .heroGlassCard.cardB{right:8%;top:29%;animation-delay:-2.1s}
        .heroGlassCard.cardC{right:15%;bottom:16%;animation-delay:-3.4s}
        .heroGlassCard.cardD{left:13%;bottom:20%;animation-delay:-4.6s}
        .heroAgentRail{
          position:absolute;
          left:50%;
          bottom:8%;
          transform:translateX(-50%);
          display:flex;
          gap:10px;
          padding:10px;
          border-radius:999px;
          border:1px solid rgba(124,116,255,.20);
          background:rgba(8,11,20,.55);
          backdrop-filter:blur(18px);
          -webkit-backdrop-filter:blur(18px);
          box-shadow:0 22px 60px rgba(0,0,0,.30);
        }
        .heroAgentDot{
          width:42px;
          height:42px;
          border-radius:999px;
          display:grid;
          place-items:center;
          color:#fff;
          font-size:12px;
          font-weight:950;
          background:linear-gradient(135deg,rgba(124,116,255,.85),rgba(14,207,188,.52));
          box-shadow:0 14px 34px rgba(91,82,240,.32);
          animation:agentPulse 2.8s ease-in-out infinite;
        }
        .heroAgentDot:nth-child(2){animation-delay:.25s}
        .heroAgentDot:nth-child(3){animation-delay:.5s}
        .heroAgentDot:nth-child(4){animation-delay:.75s}
        .heroAgentDot:nth-child(5){animation-delay:1s}
        .heroDashboardPreview{
          position:absolute;
          right:11%;
          top:46%;
          width:310px;
          border-radius:28px;
          overflow:hidden;
          border:1px solid rgba(124,116,255,.26);
          background:linear-gradient(180deg,rgba(9,15,31,.94),rgba(3,8,20,.97));
          box-shadow:0 38px 100px rgba(0,0,0,.46),0 0 80px rgba(91,82,240,.16);
          backdrop-filter:blur(18px);
          -webkit-backdrop-filter:blur(18px);
          animation:dashboardFloat 8.5s ease-in-out infinite;
        }
        .heroDashboardTop{
          height:40px;
          display:flex;
          align-items:center;
          gap:7px;
          padding:0 14px;
          border-bottom:1px solid rgba(255,255,255,.08);
          background:rgba(255,255,255,.04);
        }
        .heroDashboardTop span{
          width:9px;
          height:9px;
          border-radius:999px;
          background:#7C74FF;
        }
        .heroDashboardTop span:nth-child(2){background:#0ECFBC}
        .heroDashboardTop span:nth-child(3){background:#F59E0B}
        .heroDashboardBody{
          padding:14px;
          display:grid;
          gap:10px;
        }
        .heroMiniRow{
          display:grid;
          grid-template-columns:34px 1fr 44px;
          gap:9px;
          align-items:center;
          padding:10px;
          border:1px solid rgba(124,116,255,.16);
          background:rgba(255,255,255,.045);
          border-radius:16px;
        }
        .heroMiniIcon{
          width:34px;
          height:34px;
          border-radius:12px;
          display:grid;
          place-items:center;
          color:#C7D2FE;
          background:rgba(124,116,255,.18);
          font-size:12px;
          font-weight:950;
        }
        .heroMiniText strong{
          display:block;
          color:#fff;
          font-size:12px;
          margin-bottom:3px;
        }
        .heroMiniText span{
          display:block;
          color:#94A3B8;
          font-size:11px;
        }
        .heroMiniStatus{
          color:#0ECFBC;
          font-size:10px;
          font-weight:950;
        }
        @keyframes heroCardFloat{
          0%,100%{transform:translate3d(0,0,0) rotate(0deg)}
          50%{transform:translate3d(0,-14px,0) rotate(1deg)}
        }
        @keyframes dashboardFloat{
          0%,100%{transform:translate3d(0,0,0) rotateY(-7deg)}
          50%{transform:translate3d(0,-18px,0) rotateY(-2deg)}
        }
        @keyframes agentPulse{
          0%,100%{transform:translateY(0) scale(1);filter:brightness(1)}
          50%{transform:translateY(-7px) scale(1.05);filter:brightness(1.16)}
        }
        @media(max-width:1100px){
          .heroGlassCard,.heroDashboardPreview{display:none}
          .heroAgentRail{bottom:5%}
        }
'''

component = r'''
function HeroVisualSystem() {
  return (
    <div className="heroVisualSystem" aria-hidden="true">
      <div className="heroGlassCard cardA">
        <strong>Product Research Agent</strong>
        <span>Analyses offers, market gaps and buyer intent.</span>
        <em>Live</em>
      </div>

      <div className="heroGlassCard cardB">
        <strong>Campaign Builder</strong>
        <span>Turns business context into launch-ready execution.</span>
        <em>Generating</em>
      </div>

      <div className="heroGlassCard cardC">
        <strong>Governed Approval</strong>
        <span>High-risk actions stay locked until owner approval.</span>
        <em>Protected</em>
      </div>

      <div className="heroGlassCard cardD">
        <strong>AI Workforce</strong>
        <span>Specialist agents coordinate across ecommerce tasks.</span>
        <em>24 active</em>
      </div>

      <div className="heroDashboardPreview">
        <div className="heroDashboardTop">
          <span />
          <span />
          <span />
        </div>
        <div className="heroDashboardBody">
          {[
            ["AI", "Store strategy", "Ready"],
            ["UGC", "Video brief", "Live"],
            ["SEO", "Growth actions", "Queued"],
          ].map(([icon, title, status]) => (
            <div className="heroMiniRow" key={title}>
              <div className="heroMiniIcon">{icon}</div>
              <div className="heroMiniText">
                <strong>{title}</strong>
                <span>Premium execution layer</span>
              </div>
              <div className="heroMiniStatus">{status}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="heroAgentRail">
        {["AI", "UGC", "SEO", "ADS", "CRM"].map((item) => (
          <div className="heroAgentDot" key={item}>{item}</div>
        ))}
      </div>
    </div>
  );
}
'''

if "function HeroVisualSystem()" not in s:
    insert_at = s.find("function PremiumHeroOrb()")
    if insert_at == -1:
        raise SystemExit("FAILED: PremiumHeroOrb marker not found")
    s = s[:insert_at] + component + "\n" + s[insert_at:]

if "LANDING_HERO_VISUAL_DENSITY_V1" not in s:
    marker = "        @media(max-width:900px)"
    if marker not in s:
        raise SystemExit("FAILED: CSS marker not found")
    s = s.replace(marker, css + "\n" + marker, 1)

if "<HeroVisualSystem />" not in s:
    if "<PremiumHeroOrb />" in s:
        s = s.replace("<PremiumHeroOrb />", "<HeroVisualSystem />\n        <PremiumHeroOrb />", 1)
    elif '<div className="heroInner">' in s:
        s = s.replace('<div className="heroInner">', '<HeroVisualSystem />\n        <div className="heroInner">', 1)
    else:
        raise SystemExit("FAILED: hero insertion point not found")

TARGET.write_text(s, encoding="utf-8")

print("LANDING_HERO_VISUAL_DENSITY_UPGRADED")
print(f"Backup: {backup}")