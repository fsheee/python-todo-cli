/**
 * Landing page - shows feature showcase to unauthenticated users
 * Redirects authenticated users to chat
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import Hero from '@/components/landing/Hero';
import FeatureShowcase from '@/components/landing/FeatureShowcase';
import HowItWorks from '@/components/landing/HowItWorks';
import LiveDemo from '@/components/landing/LiveDemo';
import FinalCTA from '@/components/landing/FinalCTA';

export default function LandingPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [mounted, setMounted] = useState(false);

  // Handle hydration
  useEffect(() => {
    setMounted(true);
  }, []);

  // No auto-redirect for authenticated users - allow them to see landing page
  // They can navigate to chat via the CTA button

  // Don't render landing page until hydration complete
  if (!mounted) {
    return <div className="loading-page">Loading...</div>;
  }

  // Show landing page to users (authenticated or not)
  return (
    <main className="landing-page">
      <Hero />
      <FeatureShowcase />
      <HowItWorks />
      <LiveDemo />
      <FinalCTA />
    </main>
  );
}
