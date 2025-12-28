/**
 * Hero section for landing page
 * Pure CSS animations, no framer-motion
 */

'use client';

import Link from 'next/link';

export default function Hero() {
  const scrollToDemo = () => {
    document.getElementById('demo-section')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section className="hero-section">
      {/* Animated Background Orbs */}
      <div className="hero-background">
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
        <div className="gradient-orb orb-3"></div>
      </div>

      {/* Hero Content */}
      <div className="hero-content">
        <div className="hero-text fade-in">
          <h1 className="hero-title">
            Todo Management,
            <span className="gradient-text"> Reimagined</span>
          </h1>

          <p className="hero-subtitle">
            Just chat naturally. Your AI assistant turns
            <strong> "Add buy milk tomorrow"</strong> into reality. ✨
          </p>

          <div className="hero-actions">
            <Link href="/login">
              <button className="btn-hero-primary">
                Get Started Free
              </button>
            </Link>

            <button className="btn-hero-secondary" onClick={scrollToDemo}>
              Watch Demo
            </button>
          </div>

          {/* Feature Pills */}
          <div className="hero-features">
            <span className="feature-pill">💬 Natural Language</span>
            <span className="feature-pill">🧠 Context Aware</span>
            <span className="feature-pill">⚡ Lightning Fast</span>
          </div>
        </div>

        {/* Hero Illustration */}
        <div className="hero-visual slide-in-right">
          <div className="chat-preview">
            <div className="preview-message user-msg">
              "Add buy groceries tomorrow"
            </div>
            <div className="preview-message ai-msg">
              ✅ I've added "Buy groceries" for tomorrow!
            </div>
          </div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="scroll-indicator">
        <span>Scroll to explore</span>
        <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
          <path d="M10 14l-5-5h10l-5 5z" />
        </svg>
      </div>
    </section>
  );
}
