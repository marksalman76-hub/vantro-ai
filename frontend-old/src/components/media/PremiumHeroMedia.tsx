"use client";

import dynamic from "next/dynamic";
import { motion } from "framer-motion";

const Spline = dynamic(() => import("@splinetool/react-spline"), {
  ssr: false,
  loading: () => <PremiumMediaFallback />,
});

type PremiumHeroMediaProps = {
  videoWebm?: string;
  videoMp4?: string;
  poster?: string;
  splineScene?: string;
  mode?: "video" | "spline" | "fallback";
};

export function PremiumMediaFallback() {
  return (
    <div className="premium-media-fallback">
      <div className="premium-orbit premium-orbit-one" />
      <div className="premium-orbit premium-orbit-two" />
      <div className="premium-core">
        <span>AI</span>
      </div>
      <div className="premium-panel premium-panel-one">Strategy Agent</div>
      <div className="premium-panel premium-panel-two">Creative Agent</div>
      <div className="premium-panel premium-panel-three">Analytics Agent</div>
    </div>
  );
}

export default function PremiumHeroMedia({
  videoWebm = "/media/landing/hero/hero-command-centre.webm",
  videoMp4 = "/media/landing/hero/hero-command-centre.mp4",
  poster = "/media/landing/hero/hero-command-centre-poster.webp",
  splineScene,
  mode = "fallback",
}: PremiumHeroMediaProps) {
  if (mode === "spline" && splineScene) {
    return (
      <motion.div className="premium-media-shell" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}>
        <Spline scene={splineScene} />
      </motion.div>
    );
  }

  if (mode === "video") {
    return (
      <motion.div className="premium-media-shell" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}>
        <video className="premium-hero-video" autoPlay muted loop playsInline poster={poster}>
          <source src={videoWebm} type="video/webm" />
          <source src={videoMp4} type="video/mp4" />
        </video>
      </motion.div>
    );
  }

  return (
    <motion.div className="premium-media-shell" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}>
      <PremiumMediaFallback />
    </motion.div>
  );
}
