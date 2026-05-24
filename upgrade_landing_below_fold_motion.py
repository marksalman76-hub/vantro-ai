from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"landing_page_before_below_fold_motion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")

css = r'''
        /* LANDING_BELOW_FOLD_MOTION_POLISH_V1 */
        .agents,.platform,.pricing,.final{
          position:relative;
          overflow:hidden;
        }
        .agents:before,.platform:before,.pricing:before{
          content:"";
          position:absolute;
          inset:8% auto auto 50%;
          width:760px;
          height:760px;
          transform:translateX(-50%);
          border-radius:999px;
          background:radial-gradient(circle, rgba(124,116,255,.10), transparent 64%);
          pointer-events:none;
          filter:blur(10px);
        }
        .agentGrid,.pricingGrid{
          perspective:1300px;
        }
        .agentCard,.priceCard{
          will-change:transform;
        }
        .agentCard:hover .agentVisual{
          transform:translateY(-10px) scale(1.05) rotate(2deg);
          filter:brightness(1.16);
        }
        .agentCard h3,.priceCard h3{
          letter-spacing:-.035em;
        }
        .agentCard p,.priceCard p{
          color:#A7B0C6!important;
        }
        .platform .window{
          border-color:rgba(124,116,255,.26)!important;
        }
        .platform .window:after{
          content:"";
          position:absolute;
          inset:0;
          background:
            radial-gradient(circle at 74% 18%, rgba(14,207,188,.10), transparent 26%),
            radial-gradient(circle at 22% 74%, rgba(124,116,255,.13), transparent 30%);
          pointer-events:none;
        }
        .context div,.task,.output{
          box-shadow:inset 0 1px 0 rgba(255,255,255,.08);
        }
        .task{
          position:relative;
          overflow:hidden;
        }
        .task:after{
          content:"";
          position:absolute;
          left:0;
          bottom:0;
          height:2px;
          width:64%;
          background:linear-gradient(90deg,#7C74FF,#0ECFBC);
          animation:taskProgress 4.8s ease-in-out infinite;
        }
        .output{
          position:relative;
          overflow:hidden;
        }
        .output:after{
          content:"";
          position:absolute;
          inset:auto 14px 14px auto;
          width:72px;
          height:72px;
          border-radius:999px;
          background:radial-gradient(circle, rgba(14,207,188,.18), transparent 70%);
          filter:blur(2px);
        }
        .priceCard{
          transition:transform .28s ease, box-shadow .28s ease, border-color .28s ease;
        }
        .priceCard:hover{
          border-color:rgba(14,207,188,.30)!important;
          box-shadow:0 34px 95px rgba(0,0,0,.34),0 0 80px rgba(91,82,240,.12);
        }
        .priceCard.featured{
          transform:translateY(-8px);
          border-color:rgba(124,116,255,.46)!important;
        }
        .priceCard.featured:hover{
          transform:translateY(-14px) rotateX(2deg) rotateY(-2deg);
        }
        .final{
          border-top:1px solid rgba(124,116,255,.14);
        }
        .final:before{
          content:"";
          position:absolute;
          inset:12% 18%;
          background:radial-gradient(circle, rgba(124,116,255,.18), transparent 64%);
          filter:blur(20px);
          pointer-events:none;
        }
        .final h2{
          background:linear-gradient(135deg,#fff,#A5B4FC,#5EEAD4);
          -webkit-background-clip:text;
          background-clip:text;
          color:transparent!important;
        }
        @keyframes taskProgress{
          0%,100%{width:18%;opacity:.55}
          50%{width:92%;opacity:1}
        }
'''

if "LANDING_BELOW_FOLD_MOTION_POLISH_V1" not in s:
    marker = "        @media(max-width:900px)"
    if marker not in s:
        raise SystemExit("FAILED: CSS marker not found")
    s = s.replace(marker, css + "\n" + marker, 1)

TARGET.write_text(s, encoding="utf-8")

print("LANDING_BELOW_FOLD_MOTION_POLISH_ADDED")
print(f"Backup: {backup}")