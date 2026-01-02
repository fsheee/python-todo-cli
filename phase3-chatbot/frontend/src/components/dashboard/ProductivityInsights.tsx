/**
 * Productivity insights widget
 */

'use client';

import { TrendingUp, Flame, Calendar, Target } from 'lucide-react';

interface Insights {
  streak_days: number;
  completion_rate: number;
  most_productive_day: string;
  tasks_per_day_avg: number;
}

export default function ProductivityInsights({ insights }: { insights: Insights }) {
  if (!insights) return null;

  return (
    <div className="insights-widget">
      <h3 className="widget-title">Productivity Insights</h3>

      <div className="insights-grid">
        <div className="insight-item">
          <span className="insight-icon" style={{ color: '#f59e0b' }}>
            <Flame size={32} />
          </span>
          <div className="insight-content">
            <div className="insight-value">{insights.streak_days}</div>
            <div className="insight-label">Day Streak</div>
          </div>
        </div>

        <div className="insight-item">
          <span className="insight-icon" style={{ color: '#22c55e' }}>
            <TrendingUp size={32} />
          </span>
          <div className="insight-content">
            <div className="insight-value">{Math.round(insights.completion_rate * 100)}%</div>
            <div className="insight-label">Completion Rate</div>
          </div>
        </div>

        <div className="insight-item">
          <span className="insight-icon" style={{ color: '#8b5cf6' }}>
            <Calendar size={32} />
          </span>
          <div className="insight-content">
            <div className="insight-value">{insights.most_productive_day}</div>
            <div className="insight-label">Best Day</div>
          </div>
        </div>

        <div className="insight-item">
          <span className="insight-icon" style={{ color: '#3b82f6' }}>
            <Target size={32} />
          </span>
          <div className="insight-content">
            <div className="insight-value">{insights.tasks_per_day_avg.toFixed(1)}</div>
            <div className="insight-label">Tasks/Day</div>
          </div>
        </div>
      </div>

      {/* Motivational Message */}
      <div className="motivation-message">
        {getMotivationalMessage(insights.completion_rate, insights.streak_days)}
      </div>
    </div>
  );
}

function getMotivationalMessage(completionRate: number, streak: number): string {
  if (completionRate >= 0.9 && streak >= 7) {
    return "🌟 Outstanding! You're on fire! Keep up this amazing productivity!";
  }
  if (completionRate >= 0.7) {
    return "💪 Great work! You're staying on top of your tasks!";
  }
  if (streak >= 3) {
    return "🔥 Nice streak! Consistency is key to success!";
  }
  return "✨ You're doing great! Every completed task is progress!";
}
