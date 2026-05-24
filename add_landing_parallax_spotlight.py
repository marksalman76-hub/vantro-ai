from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"landing_page_before_parallax_spotlight_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")

component = r'''
function LandingSpotlightLayer() {
  return (
    <div className="landingSpotlightLayer" aria-hidden="true">
      <div className="spotlightBeam beamOne" />
      <div className="spotlightBeam beamTwo" />
      <div className="spotlightBeam beamThree" />
      <div className="ambientParticleField">
        {Array.from({ length: 34 }).map((_, index) => (
          <span key={index} style={{ ["--i" as any]: index }} />
        ))}
      </div>
    </div>
  );
}
'''

css = r'''
        /* LANDING_PARALLAX_SPOTLIGHT_V1 */
        .landingSpotlightLayer{
          position:fixed;
          inset:0;
          pointer-events:none;
          z-index:0;
          overflow:hidden;
        }
        .spotlightBeam{
          position:absolute;
          width:42vw;
          height:42vw;
          border-radius:999px;
          filter:blur(42px);
          opacity:.24;
          mix-blend-mode:screen;
          animation:spotlightDrift 16s ease-in-out infinite;
        }
        .beamOne{
          left:-12vw;
          top:18vh;
          background:radial-gradient(circle, rgba(124,116,255,.48), transparent 64%);
        }
        .beamTwo{
          right:-10vw;
          top:8vh;
          background:radial-gradient(circle, rgba(14,207,188,.32), transparent 66%);
          animation-delay:-5s;
        }
        .beamThree{
          left:32vw;
          bottom:-20vw;
          background:radial-gradient(circle, rgba(78,172,255,.22), transparent 70%);
          animation-delay:-9s;
        }
        .ambientParticleField{
          position:absolute;
          inset:0;
          opacity:.55;
        }
        .ambientParticleField span{
          position:absolute;
          width:3px;
          height:3px;
          border-radius:999px;
          background:rgba(255,255,255,.72);
          left:calc((var(--i) * 29px) % 100vw);
          top:calc((var(--i) * 53px) % 100vh);
          animation:particleRise calc(7s + (var(--i) * .17s)) linear infinite;
          animation-delay:calc(var(--i) * -.31s);
          box-shadow:0 0 14px rgba(124,116,255,.42);
        }
        .heroGlassCard.cardA{transform:translateY(var(--scroll-shift-a,0px))}
        .heroGlassCard.cardB{transform:translateY(var(--scroll-shift-b,0px))}
        .heroDashboardPreview{transform:translateY(var(--scroll-shift-c,0px))}
        .heroAgentRail{transform:translateX(-50%) translateY(var(--scroll-shift-d,0px))}
        @keyframes spotlightDrift{
          0%,100%{transform:translate3d(0,0,0) scale(1)}
          50%{transform:translate3d(4vw,-4vh,0) scale(1.12)}
        }
        @keyframes particleRise{
          from{transform:translateY(18vh);opacity:0}
          16%{opacity:.7}
          82%{opacity:.45}
          to{transform:translateY(-110vh);opacity:0}
        }
'''

if "function LandingSpotlightLayer()" not in s:
    insert_at = s.find("function HeroVisualSystem()")
    if insert_at == -1:
        raise SystemExit("FAILED: HeroVisualSystem marker not found")
    s = s[:insert_at] + component + "\n" + s[insert_at:]

if "LANDING_PARALLAX_SPOTLIGHT_V1" not in s:
    marker = "        @media(max-width:900px)"
    if marker not in s:
        raise SystemExit("FAILED: CSS marker not found")
    s = s.replace(marker, css + "\n" + marker, 1)

if "<LandingSpotlightLayer />" not in s:
    marker = "<main>"
    if marker in s:
      s = s.replace(marker, "<main>\n      <LandingSpotlightLayer />", 1)
    else:
      raise SystemExit("FAILED: main marker not found")

TARGET.write_text(s, encoding="utf-8")

print("LANDING_PARALLAX_SPOTLIGHT_ADDED")
print(f"Backup: {backup}")