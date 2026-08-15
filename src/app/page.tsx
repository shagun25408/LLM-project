"use client";

import LiquidMetalHero from "@/components/ui/liquid-metal-hero";

export default function Home() {
  return (
    <LiquidMetalHero
      badge="AI-Powered Cybersecurity"
      title="CyberGuard AI"
      subtitle="Detect, analyze, and respond to evolving cyber threats with intelligent security built for modern teams."
      primaryCtaLabel="Secure Your Business"
      secondaryCtaLabel="Explore Platform"
      onPrimaryCtaClick={() => (window.location.href = "/dashboard")}
      onSecondaryCtaClick={() => alert("Examples coming soon.")}
      features={["Real-Time Threat Detection",
  "AI-Powered Analysis",
  "24/7 Security Monitoring"]}
    />
  );
}
