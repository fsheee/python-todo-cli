/**
 * Recent activity feed showing last todo actions
 */

'use client';

interface Activity {
  id: number;
  action: 'created' | 'completed' | 'updated' | 'deleted';
  todo_title: string;
  timestamp: string;
}

const actionIcons: Record<string, string> = {
  created: '➕',
  completed: '✅',
  updated: '✏️',
  deleted: '🗑️'
};

const actionLabels: Record<string, string> = {
  created: 'Created',
  completed: 'Completed',
  updated: 'Updated',
  deleted: 'Deleted'
};

const actionColors: Record<string, string> = {
  created: '#3b82f6',
  completed: '#22c55e',
  updated: '#f59e0b',
  deleted: '#ef4444'
};

export default function RecentActivity({ activities }: { activities: Activity[] }) {
  if (!activities || activities.length === 0) {
    return (
      <div className="activity-widget">
        <h3 className="widget-title">Recent Activity</h3>
        <p className="empty-state">No recent activity</p>
      </div>
    );
  }

  return (
    <div className="activity-widget">
      <h3 className="widget-title">Recent Activity</h3>

      <div className="activity-list">
        {activities.map((activity) => (
          <div key={activity.id} className="activity-item">
            <span
              className="activity-icon"
              style={{ color: actionColors[activity.action] }}
            >
              {actionIcons[activity.action]}
            </span>
            <span className="activity-text">
              <strong>{actionLabels[activity.action]}</strong> "{activity.todo_title}"
            </span>
            <span className="activity-time">{formatTime(activity.timestamp)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function formatTime(timestamp: string): string {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = Math.floor((now.getTime() - date.getTime()) / 60000);

  if (diff < 1) return 'Just now';
  if (diff < 60) return `${diff}m ago`;
  if (diff < 1440) return `${Math.floor(diff / 60)}h ago`;
  return `${Math.floor(diff / 1440)}d ago`;
}
