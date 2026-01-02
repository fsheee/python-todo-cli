/**
 * Dashboard page - Shows todo analytics and insights
 * Protected route - requires authentication
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import DashboardHeader from '@/components/dashboard/DashboardHeader';
import QuickStatsCards from '@/components/dashboard/QuickStatsCards';
import RecentActivity from '@/components/dashboard/RecentActivity';
import ProductivityInsights from '@/components/dashboard/ProductivityInsights';

interface DashboardData {
  summary: {
    total: number;
    pending: number;
    completed_today: number;
    overdue: number;
  };
  recent_activity: Array<{
    id: number;
    action: 'created' | 'completed' | 'updated' | 'deleted';
    todo_title: string;
    timestamp: string;
  }>;
  insights: {
    streak_days: number;
    completion_rate: number;
    most_productive_day: string;
    tasks_per_day_avg: number;
  };
}

export default function DashboardPage() {
  const { isAuthenticated } = useAuthStore();
  const router = useRouter();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Auth check
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  // Load dashboard data
  useEffect(() => {
    if (isAuthenticated) {
      loadDashboardData();
    }
  }, [isAuthenticated]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // For now, use mock data (backend endpoints to be created)
      // TODO: Replace with real API calls when backend is ready
      const mockData: DashboardData = {
        summary: {
          total: 25,
          pending: 15,
          completed_today: 3,
          overdue: 2
        },
        recent_activity: [
          {
            id: 1,
            action: 'completed',
            todo_title: 'Buy groceries',
            timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
          },
          {
            id: 2,
            action: 'created',
            todo_title: 'Call dentist',
            timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString()
          },
          {
            id: 3,
            action: 'updated',
            todo_title: 'Finish quarterly report',
            timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()
          }
        ],
        insights: {
          streak_days: 7,
          completion_rate: 0.85,
          most_productive_day: 'Monday',
          tasks_per_day_avg: 5.2
        }
      };

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500));

      setData(mockData);
    } catch (err: any) {
      console.error('Failed to load dashboard:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return <div className="loading-page">Redirecting...</div>;
  }

  if (loading) {
    return (
      <div className="dashboard-page">
        <DashboardHeader />
        <div className="loading-page">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-page">
        <DashboardHeader />
        <div className="error-page">
          <p>{error}</p>
          <button onClick={loadDashboardData} className="btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      <DashboardHeader />

      <main className="dashboard-main">
        {data && (
          <>
            <QuickStatsCards stats={data.summary} />
            <div className="dashboard-widgets">
              <RecentActivity activities={data.recent_activity} />
              <ProductivityInsights insights={data.insights} />
            </div>
          </>
        )}
      </main>
    </div>
  );
}
