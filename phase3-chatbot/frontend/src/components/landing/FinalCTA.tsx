/**
 * Final call-to-action section for landing page
 */

'use client';

import Link from 'next/link';

export default function FinalCTA() {
  return (
    <section className="final-cta-section">
      <div className="cta-container">
        <div className="cta-content fade-in">
          <h2 className="cta-title">Ready to Get Started?</h2>
          <p className="cta-subtitle">
            Join thousands managing their todos effortlessly with AI
          </p>

          <div className="cta-actions">
            <Link href="/login">
              <button className="btn-cta-primary">
                Start Free Today
              </button>
            </Link>

            <p className="cta-note">No credit card required • Free forever</p>
          </div>
        </div>

        {/* Decorative element */}
        <div className="cta-decoration">
          <div className="decoration-orb"></div>
        </div>
      </div>
    </section>
  );
}
