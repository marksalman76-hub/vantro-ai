from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"landing_page_before_animations_glass_3d_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")

effects = r'''
        /* LANDING_PREMIUM_ANIMATION_GLASS_3D_V1 */
        main{
          position:relative;
          background:
            radial-gradient(circle at 18% 4%, rgba(124,116,255,.18), transparent 26%),
            radial-gradient(circle at 84% 10%, rgba(14,207,188,.12), transparent 28%),
            linear-gradient(180deg,#050814 0%,#080B14 46%,#060916 100%);
        }
        main:before{
          content:"";
          position:fixed;
          inset:0;
          pointer-events:none;
          z-index:0;
          background:
            radial-gradient(circle at 20% 20%, rgba(124,116,255,.16), transparent 18%),
            radial-gradient(circle at 80% 30%, rgba(14,207,188,.10), transparent 20%),
            linear-gradient(rgba(255,255,255,.025) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,.025) 1px, transparent 1px);
          background-size:auto,auto,72px 72px,72px 72px;
          mask-image:linear-gradient(180deg,black 0%,rgba(0,0,0,.68) 42%,transparent 100%);
        }
        main > *{position:relative;z-index:1}
        .nav{
          background:rgba(8,11,20,.68)!important;
          backdrop-filter:blur(26px) saturate(150%)!important;
          -webkit-backdrop-filter:blur(26px) saturate(150%)!important;
          box-shadow:0 18px 50px rgba(0,0,0,.22);
        }
        .logo,.navBtn,.primary,.secondary,.priceCard a,.final a{
          transition:transform .22s ease, box-shadow .22s ease, border-color .22s ease, filter .22s ease;
        }
        .logo:hover,.navBtn:hover,.primary:hover,.secondary:hover,.priceCard a:hover,.final a:hover{
          transform:translateY(-2px);
          filter:brightness(1.08);
          box-shadow:0 18px 42px rgba(91,82,240,.28);
        }
        .hero{
          perspective:1200px;
          isolation:isolate;
        }
        .hero:before{
          content:"";
          position:absolute;
          width:min(86vw,980px);
          height:min(86vw,980px);
          border-radius:999px;
          background:conic-gradient(from 180deg, rgba(124,116,255,.20), rgba(14,207,188,.12), rgba(78,172,255,.10), rgba(124,116,255,.20));
          filter:blur(28px);
          opacity:.36;
          animation:slowSpin 28s linear infinite;
          transform:translateZ(-1px);
        }
        .hero:after{
          content:"";
          position:absolute;
          width:520px;
          height:520px;
          right:7%;
          bottom:11%;
          border-radius:999px;
          background:radial-gradient(circle, rgba(14,207,188,.20), transparent 64%);
          filter:blur(8px);
          animation:floatOrb 9s ease-in-out infinite;
        }
        .heroInner{
          transform-style:preserve-3d;
          animation:heroLift .9s ease both;
        }
        .eyebrow{
          backdrop-filter:blur(16px);
          -webkit-backdrop-filter:blur(16px);
          box-shadow:inset 0 1px 0 rgba(255,255,255,.12), 0 18px 46px rgba(91,82,240,.18);
        }
        h1{
          text-shadow:0 18px 70px rgba(124,116,255,.20);
        }
        .h1-line2{
          display:inline-block;
          background:linear-gradient(135deg,#fff 0%,#9D97FF 36%,#0ECFBC 76%,#fff 100%);
          background-size:220% auto;
          -webkit-background-clip:text;
          background-clip:text;
          color:transparent;
          animation:textSheen 5.8s ease-in-out infinite;
        }
        .primary{
          background:linear-gradient(135deg,#5B52F0,#7C74FF,#0ECFBC)!important;
          background-size:180% auto!important;
          animation:ctaPulse 5.5s ease-in-out infinite;
        }
        .secondary,.agentCard,.priceCard,.window,.context div,.task,.output{
          backdrop-filter:blur(18px) saturate(145%);
          -webkit-backdrop-filter:blur(18px) saturate(145%);
        }
        .numbers div,.agentCard,.priceCard,.window{
          transform-style:preserve-3d;
        }
        .numbers div{
          transition:transform .25s ease, background .25s ease;
        }
        .numbers div:hover{
          transform:translateY(-4px);
          background:rgba(255,255,255,.025);
        }
        .agentCard,.priceCard{
          position:relative;
          overflow:hidden;
          background:linear-gradient(180deg,rgba(255,255,255,.075),rgba(255,255,255,.035))!important;
          box-shadow:inset 0 1px 0 rgba(255,255,255,.08), 0 24px 70px rgba(0,0,0,.22);
        }
        .agentCard:before,.priceCard:before,.window:before{
          content:"";
          position:absolute;
          inset:-1px;
          background:linear-gradient(120deg,transparent 0%,rgba(255,255,255,.16) 22%,transparent 44%);
          transform:translateX(-130%);
          transition:transform .75s ease;
          pointer-events:none;
        }
        .agentCard:hover:before,.priceCard:hover:before,.window:hover:before{
          transform:translateX(130%);
        }
        .agentCard:hover,.priceCard:hover{
          transform:translateY(-8px) rotateX(2deg) rotateY(-2deg);
        }
        .agentVisual{
          box-shadow:inset 0 1px 0 rgba(255,255,255,.16), 0 20px 50px color-mix(in srgb, var(--accent) 28%, transparent);
          animation:softFloat 7s ease-in-out infinite;
        }
        .agentCard:nth-child(2n) .agentVisual{animation-delay:-1.2s}
        .agentCard:nth-child(3n) .agentVisual{animation-delay:-2.3s}
        .platform{
          perspective:1300px;
        }
        .window{
          position:relative;
          background:linear-gradient(180deg,rgba(15,22,37,.92),rgba(5,10,22,.96))!important;
          transform:rotateX(2deg) rotateY(-4deg);
          transition:transform .35s ease, box-shadow .35s ease;
        }
        .window:hover{
          transform:rotateX(0deg) rotateY(0deg) translateY(-6px);
          box-shadow:0 42px 110px rgba(0,0,0,.78), 0 0 70px rgba(91,82,240,.16);
        }
        .windowTop{
          backdrop-filter:blur(18px);
          -webkit-backdrop-filter:blur(18px);
        }
        .pills span,.context div,.task,.output{
          transition:transform .22s ease, border-color .22s ease, background .22s ease;
        }
        .pills span:hover,.context div:hover,.task:hover,.output:hover{
          transform:translateY(-2px);
          border-color:rgba(124,116,255,.28);
          background:rgba(255,255,255,.07);
        }
        .premium-media-landing-marker{
          position:relative;
          overflow:hidden;
          background:
            radial-gradient(circle at 74% 22%, rgba(14,207,188,.11), transparent 24%),
            radial-gradient(circle at 18% 70%, rgba(124,116,255,.12), transparent 26%),
            #080B14!important;
        }
        .premium-media-landing-marker:before{
          content:"";
          position:absolute;
          inset:0;
          background:linear-gradient(115deg,transparent,rgba(255,255,255,.06),transparent);
          transform:translateX(-100%);
          animation:sectionSweep 9s ease-in-out infinite;
        }
        .priceCard.featured{
          box-shadow:0 28px 80px rgba(91,82,240,.26), inset 0 1px 0 rgba(255,255,255,.10);
        }
        .final{
          position:relative;
          overflow:hidden;
          background:
            radial-gradient(circle at 50% 10%, rgba(124,116,255,.18), transparent 28%),
            linear-gradient(180deg,transparent,rgba(255,255,255,.018));
        }
        @keyframes heroLift{
          from{opacity:0;transform:translateY(28px) scale(.985)}
          to{opacity:1;transform:translateY(0) scale(1)}
        }
        @keyframes slowSpin{
          to{transform:rotate(360deg)}
        }
        @keyframes floatOrb{
          0%,100%{transform:translate3d(0,0,0) scale(1)}
          50%{transform:translate3d(-24px,-30px,0) scale(1.08)}
        }
        @keyframes textSheen{
          0%,100%{background-position:0% center}
          50%{background-position:100% center}
        }
        @keyframes ctaPulse{
          0%,100%{background-position:0% center;box-shadow:0 18px 44px rgba(91,82,240,.26)}
          50%{background-position:100% center;box-shadow:0 24px 62px rgba(14,207,188,.20)}
        }
        @keyframes softFloat{
          0%,100%{transform:translateY(0)}
          50%{transform:translateY(-8px)}
        }
        @keyframes sectionSweep{
          0%,72%{transform:translateX(-110%)}
          100%{transform:translateX(110%)}
        }
        @media (prefers-reduced-motion: reduce){
          *,*:before,*:after{
            animation:none!important;
            transition:none!important;
            scroll-behavior:auto!important;
          }
        }
'''

if "LANDING_PREMIUM_ANIMATION_GLASS_3D_V1" in s:
    print("Landing effects already installed.")
else:
    marker = "        @media(max-width:900px)"
    if marker not in s:
        raise SystemExit("FAILED: CSS media marker not found")
    s = s.replace(marker, effects + "\n" + marker, 1)
    TARGET.write_text(s, encoding="utf-8")
    print("LANDING_ANIMATIONS_GLASS_3D_ADDED")

print(f"Backup: {backup}")