from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
TARGET = ROOT / "frontend" / "src" / "app" / "page.tsx"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

backup = BACKUP_DIR / f"landing_page_before_motion_runtime_layer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx"
shutil.copy2(TARGET, backup)

s = TARGET.read_text(encoding="utf-8")

if "LANDING_MOTION_RUNTIME_LAYER_V1" not in s:
    if '"use client";' not in s:
        s = '"use client";\n\n' + s

    imports = '''import { motion, useScroll, useTransform } from "framer-motion";
import { Canvas } from "@react-three/fiber";
import { Float, MeshDistortMaterial, OrbitControls, Stars } from "@react-three/drei";
import { Sparkles, ShieldCheck, Workflow, WandSparkles } from "lucide-react";
'''
    if 'from "framer-motion"' not in s:
        first_import = s.find("import ")
        if first_import == -1:
            s = s.replace('"use client";\n\n', '"use client";\n\n' + imports + "\n", 1)
        else:
            s = s[:first_import] + imports + s[first_import:]

    component_block = r'''
function PremiumHeroOrb() {
  return (
    <div className="heroOrb3d" aria-hidden="true">
      <Canvas camera={{ position: [0, 0, 4.2], fov: 46 }}>
        <ambientLight intensity={0.7} />
        <pointLight position={[3, 4, 5]} intensity={1.8} />
        <pointLight position={[-4, -2, 3]} intensity={0.8} color="#0ECFBC" />
        <Stars radius={42} depth={24} count={900} factor={3.4} saturation={0} fade speed={0.7} />
        <Float speed={2.2} rotationIntensity={1.1} floatIntensity={1.8}>
          <mesh>
            <sphereGeometry args={[1.25, 96, 96]} />
            <MeshDistortMaterial
              color="#7C74FF"
              emissive="#23195f"
              roughness={0.18}
              metalness={0.35}
              distort={0.34}
              speed={1.55}
            />
          </mesh>
        </Float>
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.8} />
      </Canvas>
    </div>
  );
}

function MotionBadge({ icon, title, body, delay }: { icon: React.ReactNode; title: string; body: string; delay: number }) {
  return (
    <motion.div
      className="motionBadge glassLift"
      initial={{ opacity: 0, y: 24, scale: 0.96 }}
      whileInView={{ opacity: 1, y: 0, scale: 1 }}
      viewport={{ once: true, amount: 0.25 }}
      transition={{ duration: 0.62, delay, ease: [0.22, 1, 0.36, 1] }}
      whileHover={{ y: -6, rotateX: 4, rotateY: -4 }}
    >
      <div className="motionBadgeIcon">{icon}</div>
      <div>
        <strong>{title}</strong>
        <span>{body}</span>
      </div>
    </motion.div>
  );
}

function LandingMotionRuntimeLayer() {
  return (
    <section className="motionRuntimeLayer">
      <motion.div
        className="motionRuntimeHeader"
        initial={{ opacity: 0, y: 26 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.28 }}
        transition={{ duration: 0.7 }}
      >
        <div className="runtimeEyebrow">Premium execution layer</div>
        <h2>Designed to feel like a live AI operating system, not a static SaaS page.</h2>
        <p>
          Animated workflow depth, glass panels, 3D motion, governed automation cues,
          and premium AI workforce storytelling for high-converting ecommerce clients.
        </p>
      </motion.div>

      <div className="motionRuntimeGrid">
        <MotionBadge
          delay={0.05}
          icon={<Sparkles size={20} />}
          title="Cinematic AI interface"
          body="Layered motion, glow, glass and depth for a premium product feel."
        />
        <MotionBadge
          delay={0.12}
          icon={<Workflow size={20} />}
          title="Workflow storytelling"
          body="Visualise agents moving from task to output to governed delivery."
        />
        <MotionBadge
          delay={0.19}
          icon={<ShieldCheck size={20} />}
          title="Governance visible"
          body="Approval, safety and audit confidence built into the visual language."
        />
        <MotionBadge
          delay={0.26}
          icon={<WandSparkles size={20} />}
          title="Conversion polish"
          body="Premium interactions, hover states and animated trust cues."
        />
      </div>
    </section>
  );
}
'''
    if "function LandingMotionRuntimeLayer()" not in s:
        insert_at = s.find("export default")
        if insert_at == -1:
            raise SystemExit("FAILED: export default marker not found")
        s = s[:insert_at] + component_block + "\n" + s[insert_at:]

    css = r'''
        /* LANDING_MOTION_RUNTIME_LAYER_V1 */
        .heroOrb3d{
          position:absolute;
          right:min(6vw,90px);
          top:120px;
          width:min(42vw,520px);
          height:min(42vw,520px);
          opacity:.92;
          filter:drop-shadow(0 34px 90px rgba(91,82,240,.22));
          pointer-events:none;
          z-index:0;
        }
        .heroInner{position:relative;z-index:2}
        .motionRuntimeLayer{
          position:relative;
          max-width:1180px;
          margin:40px auto 0;
          padding:56px 24px;
          z-index:2;
        }
        .motionRuntimeHeader{
          max-width:820px;
          margin:0 auto 28px;
          text-align:center;
        }
        .runtimeEyebrow{
          display:inline-flex;
          padding:9px 13px;
          border-radius:999px;
          border:1px solid rgba(124,116,255,.28);
          background:rgba(124,116,255,.12);
          color:#BDB8FF;
          font-size:12px;
          font-weight:900;
          letter-spacing:.12em;
          text-transform:uppercase;
          margin-bottom:16px;
          backdrop-filter:blur(18px);
        }
        .motionRuntimeHeader h2{
          margin:0;
          font-size:clamp(32px,5vw,58px);
          line-height:.98;
          letter-spacing:-.06em;
          color:#fff;
        }
        .motionRuntimeHeader p{
          margin:18px auto 0;
          max-width:700px;
          color:#A7B0C6;
          line-height:1.65;
          font-size:16px;
        }
        .motionRuntimeGrid{
          display:grid;
          grid-template-columns:repeat(4,minmax(0,1fr));
          gap:16px;
          perspective:1200px;
        }
        .motionBadge{
          min-height:188px;
          border:1px solid rgba(124,116,255,.20);
          border-radius:26px;
          padding:22px;
          background:linear-gradient(180deg,rgba(255,255,255,.075),rgba(255,255,255,.032));
          box-shadow:inset 0 1px 0 rgba(255,255,255,.10),0 28px 70px rgba(0,0,0,.24);
          transform-style:preserve-3d;
        }
        .motionBadgeIcon{
          width:44px;
          height:44px;
          display:grid;
          place-items:center;
          border-radius:16px;
          background:linear-gradient(135deg,rgba(124,116,255,.28),rgba(14,207,188,.14));
          color:#C7D2FE;
          margin-bottom:18px;
          box-shadow:0 18px 40px rgba(91,82,240,.20);
        }
        .motionBadge strong{
          display:block;
          color:#fff;
          font-size:17px;
          letter-spacing:-.02em;
          margin-bottom:8px;
        }
        .motionBadge span{
          display:block;
          color:#A7B0C6;
          font-size:14px;
          line-height:1.55;
        }
        .glassLift{
          backdrop-filter:blur(20px) saturate(150%);
          -webkit-backdrop-filter:blur(20px) saturate(150%);
        }
        @media(max-width:980px){
          .heroOrb3d{position:relative;right:auto;top:auto;margin:20px auto 0;width:86vw;height:360px}
          .motionRuntimeGrid{grid-template-columns:repeat(2,minmax(0,1fr))}
        }
        @media(max-width:640px){
          .motionRuntimeGrid{grid-template-columns:1fr}
        }
'''
    if "LANDING_MOTION_RUNTIME_LAYER_V1" not in s:
        marker = "        @media(max-width:900px)"
        if marker not in s:
            raise SystemExit("FAILED: CSS marker not found")
        s = s.replace(marker, css + "\n" + marker, 1)

    # Insert 3D orb into hero section if class exists.
    if "<PremiumHeroOrb />" not in s:
        if '<div className="heroInner">' in s:
            s = s.replace('<div className="heroInner">', '<PremiumHeroOrb />\n        <div className="heroInner">', 1)

    # Insert runtime layer before pricing/final if possible.
    if "<LandingMotionRuntimeLayer />" not in s:
        if '<section className="pricing"' in s:
            s = s.replace('<section className="pricing"', '<LandingMotionRuntimeLayer />\n\n      <section className="pricing"', 1)
        elif '<section className="final"' in s:
            s = s.replace('<section className="final"', '<LandingMotionRuntimeLayer />\n\n      <section className="final"', 1)
        else:
            raise SystemExit("FAILED: insertion point for runtime layer not found")

    TARGET.write_text(s, encoding="utf-8")
    print("LANDING_MOTION_RUNTIME_LAYER_ADDED")
else:
    print("Landing motion runtime layer already installed.")

print(f"Backup: {backup}")