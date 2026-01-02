/**
 * Quick stats cards showing todo counts
 */

'use client';

interface StatsCardProps {
  icon: string;
  label: string;
  value: number;
  color: string;
  trend?: string;
}

function StatCard({ icon, label, value, color, trend }: StatsCardProps) {
  return (
    <div className="stat-card" style={{ borderLeft: `4px solid ${color}` }}>
      <div className="stat-icon">{icon}</div>
      <div className="stat-content">
        <div className="stat-value">{value}</div>
        <div className="stat-label">{label}</div>
        {trend && <div className="stat-trend">{trend}</div>}
      </div>
    </div>
  );
}

interface QuickStatsProps {
  stats: {
    total: number;
    pending: number;
    completed_today: number;
    overdue: number;
  };
}

export default function QuickStatsCards({ stats }: QuickStatsProps) {
  if (!stats) return null;

  return (
    <div className="quick-stats-section">
      <div className="quick-stats-grid">
        <StatCard
          icon="📋"
          label="Pending Tasks"
          value={stats.pending}
          color="#3b82f6"
        />

        <StatCard
          icon="✅"
          label="Completed Today"
          value={stats.completed_today}
          color="#22c55e"
          trend="+2 from yesterday"
        />

        <StatCard
          icon="⚠️"
          label="Overdue"
          value={stats.overdue}
          color="#ef4444"
        />

        <StatCard
          icon="📊"
          label="Total Tasks"
          value={stats.total}
          color="#8b5cf6"
        />
      </div>
    </div>
  );
}
