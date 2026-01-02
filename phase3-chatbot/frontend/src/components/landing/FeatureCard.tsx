/**
 * Feature card component
 * Pure CSS animations, no framer-motion
 */

'use client';

interface FeatureCardProps {
  icon: string;
  title: string;
  description: string;
  example: string;
  color: string;
  index: number;
}

export default function FeatureCard({
  icon,
  title,
  description,
  example,
  color,
  index
}: FeatureCardProps) {
  return (
    <div
      className="feature-card"
      style={{
        animationDelay: `${index * 0.1}s`
      }}
    >
      <div className="feature-icon" style={{ background: color }}>
        {icon}
      </div>

      <h3 className="feature-title">{title}</h3>
      <p className="feature-description">{description}</p>

      <div className="feature-example">
        <code>{example}</code>
      </div>
    </div>
  );
}
