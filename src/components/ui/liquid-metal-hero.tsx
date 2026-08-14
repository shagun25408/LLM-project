"use client";

import { LiquidMetal, liquidMetalPresets } from "@paper-design/shaders-react";
import { motion } from "framer-motion";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface LiquidMetalHeroProps {
  badge?: string;
  title: string;
  subtitle: string;
  primaryCtaLabel: string;
  secondaryCtaLabel?: string;
  onPrimaryCtaClick: () => void;
  onSecondaryCtaClick?: () => void;
  features?: string[];
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { delayChildren: 0.2, staggerChildren: 0.15 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0 },
};

export default function LiquidMetalHero({
  badge,
  title,
  subtitle,
  primaryCtaLabel,
  secondaryCtaLabel,
  onPrimaryCtaClick,
  onSecondaryCtaClick,
  features = [],
}: LiquidMetalHeroProps) {
  return (
    <section className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#090909] text-white">
      <LiquidMetal {...liquidMetalPresets[2]} style={{ position: "fixed", inset: 0, zIndex: 0 }} />
      <div className="absolute inset-0 z-[1] bg-black/25" aria-hidden="true" />

      <div className="relative z-10 mx-auto w-full max-w-7xl px-6 py-20 lg:px-8">
        <motion.div
          className="space-y-8 text-center"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          transition={{ duration: 0.8, ease: [0.25, 0.1, 0.25, 1] }}
        >
          {badge && (
            <motion.div className="flex justify-center" variants={itemVariants}>
              <Badge variant="secondary">{badge}</Badge>
            </motion.div>
          )}

          <motion.div className="space-y-6" variants={itemVariants}>
            <h1 className="text-5xl font-bold leading-tight tracking-tight sm:text-6xl lg:text-7xl xl:text-8xl">{title}</h1>
            <p className="mx-auto max-w-3xl text-xl leading-relaxed text-white/90 sm:text-2xl">{subtitle}</p>
          </motion.div>

          <motion.div className="flex flex-col items-center justify-center gap-4 sm:flex-row" variants={itemVariants}>
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button onClick={onPrimaryCtaClick} size="lg" className="px-8 py-6 text-lg shadow-2xl">
                {primaryCtaLabel}
              </Button>
            </motion.div>
            {secondaryCtaLabel && onSecondaryCtaClick && (
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button onClick={onSecondaryCtaClick} variant="outline" size="lg" className="bg-black/10 px-8 py-6 text-lg backdrop-blur-sm">
                  {secondaryCtaLabel}
                </Button>
              </motion.div>
            )}
          </motion.div>

          {features.length > 0 && (
            <motion.div className="pt-10 sm:pt-12" variants={itemVariants}>
              <Card className="mx-auto max-w-4xl bg-black/25 backdrop-blur-md">
                <div className="grid grid-cols-1 gap-4 p-6 sm:grid-cols-3 sm:gap-6 sm:p-8">
                  {features.map((feature) => (
                    <p key={feature} className="text-center text-base font-medium text-white/90 sm:text-lg">
                      {feature}
                    </p>
                  ))}
                </div>
              </Card>
            </motion.div>
          )}
        </motion.div>
      </div>
    </section>
  );
}
