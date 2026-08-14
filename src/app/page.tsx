"use client";

import LiquidMetalHero from "@/components/ui/liquid-metal-hero";

export default function Home() {
  return (
    <LiquidMetalHero
      badge="Next-generation UI"
      title="CyberGuard AI"
      subtitle="Experience a responsive interface that flows, adapts, and makes a lasting first impression."
      primaryCtaLabel="Start Building"
      secondaryCtaLabel="View Examples"
      onPrimaryCtaClick={() => alert("Let’s start building!")}
      onSecondaryCtaClick={() => alert("Examples coming soon.")}
      features={["Seamless animations", "Responsive by design", "Modern architecture"]}
    />
  );
}
