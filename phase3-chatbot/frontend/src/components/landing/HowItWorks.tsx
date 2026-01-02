/**
 * How It Works section
 * Pure CSS animations, no framer-motion
 */

'use client';

import { MessageSquare, Brain, CheckCircle } from 'lucide-react';

const steps = [
  {
    number: 1,
    icon: MessageSquare,
    title: 'Chat Naturally',
    description: 'Just type what you need in plain English. No forms, no clicking.',
    color: '#667eea'
  },
  {
    number: 2,
    icon: Brain,
    title: 'AI Understands',
    description: 'Your assistant recognizes intent and extracts details automatically.',
    color: '#f093fb'
  },
  {
    number: 3,
    icon: CheckCircle,
    title: 'Get Things Done',
    description: 'Tasks created, updated, and tracked. Focus on what matters.',
    color: '#22c55e'
  }
];

export default function HowItWorks() {
  return (
    <section className="how-it-works-section">
      <div className="section-container">
        <div className="section-header fade-in">
          <h2 className="section-title">How It Works</h2>
          <p className="section-subtitle">
            Three simple steps to effortless task management
          </p>
        </div>

        <div className="steps-container">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <div
                key={step.number}
                className="step-card"
                style={{ animationDelay: `${index * 0.2}s` }}
              >
                <div className="step-number" style={{ background: step.color }}>
                  {step.number}
                </div>

                <div className="step-icon" style={{ color: step.color }}>
                  <Icon size={40} />
                </div>

                <h3 className="step-title">{step.title}</h3>
                <p className="step-description">{step.description}</p>

                {/* Arrow connector */}
                {index < steps.length - 1 && (
                  <div className="step-arrow">→</div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
