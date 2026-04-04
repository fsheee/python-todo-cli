/**
 * Landing page navigation bar
 */

'use client';

import Link from 'next/link';
import { useAuthStore } from '@/stores/authStore';
import { useEffect, useState } from 'react';

export default function LandingNav() {
  const { isAuthenticated } = useAuthStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <nav className="landing-nav">
      <div className="landing-nav-inner">
        <Link href="/" className="landing-nav-logo">
          <span className="logo-icon">✨</span>
          <span className="logo-text">Todo AI</span>
        </Link>
        <div className="landing-nav-spacer"></div>
        {mounted && isAuthenticated ? (
          <Link href="/chat" className="landing-nav-btn-primary">
            Go to Chat
          </Link>
        ) : (
          <>
            <Link href="/login" className="landing-nav-btn">
              Log in
            </Link>
            <Link href="/signup" className="landing-nav-btn-primary">
              Sign up
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
