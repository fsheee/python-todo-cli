/**
 * Feature showcase section for landing page
 * Displays 6 feature cards in grid layout
 */

'use client';

import FeatureCard from './FeatureCard';

const features = [
  {
    icon: '💬',
    title: 'Natural Language',
    description: 'Talk like a human, not a robot',
    example: '"Add buy milk tomorrow"',
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  },
  {
    icon: '🧠',
    title: 'Context Aware',
    description: 'Remembers your conversation',
    example: '"Make it high priority"',
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  },
  {
    icon: '⚡',
    title: 'Lightning Fast',
    description: 'Instant responses, smooth experience',
    example: 'Sub-second AI replies',
    color: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
  },
  {
    icon: '🎯',
    title: 'Smart Filters',
    description: 'Find what matters quickly',
    example: '"What\'s due today?"',
    color: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
  },
  {
    icon: '✅',
    title: 'Easy Completions',
    description: 'Mark done with a sentence',
    example: '"I finished the groceries"',
    color: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
  },
  {
    icon: '🔍',
    title: 'Powerful Search',
    description: 'Find anything instantly',
    example: '"Find work tasks"',
    color: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
  },
];

export default function FeatureShowcase() {
  return (
    <section className="feature-section">
      <div className="section-container">
        <div className="section-header">
          <h2 className="section-title">Everything You Need</h2>
          <p className="section-subtitle">
            Powerful features that make todo management effortless
          </p>
        </div>

        <div className="feature-grid">
          {features.map((feature, index) => (
            <FeatureCard
              key={index}
              {...feature}
              index={index}
            />
          ))}
        </div>
      </div>
    </section>
  );
}
