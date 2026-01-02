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

  // Redirect authenticated users to chat
  useEffect(() => {
    if (mounted && isAuthenticated) {
      router.push('/chat');
    }
  }, [isAuthenticated, mounted, router]);

  // Don't render landing page for authenticated users
  if (!mounted) {
    return <div className="loading-page">Loading...</div>;
  }

  if (isAuthenticated) {
    return <div className="loading-page">Redirecting to chat...</div>;
  }

  // Show landing page to unauthenticated users
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
