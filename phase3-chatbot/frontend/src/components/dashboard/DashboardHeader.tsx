/**
 * Dashboard header with navigation
 */

'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { BarChart3, MessageSquare, LogOut } from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';

export default function DashboardHeader() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    <header className="dashboard-header">
      <div className="dashboard-nav">
        <div className="nav-brand">
          <span className="nav-logo">✨</span>
          <h1 className="nav-title">Todo Assistant</h1>
        </div>

        <div className="nav-links">
          <Link
            href="/dashboard"
            className={pathname === '/dashboard' ? 'nav-item active' : 'nav-item'}
          >
            <BarChart3 size={20} />
            <span>Dashboard</span>
          </Link>

          <Link
            href="/chat"
            className={pathname === '/chat' ? 'nav-item active' : 'nav-item'}
          >
            <MessageSquare size={20} />
            <span>Chat</span>
          </Link>
        </div>
      </div>

      <div className="dashboard-actions">
        {user && (
          <div className="user-info">
            <div className="user-avatar">
              {user.email.charAt(0).toUpperCase()}
            </div>
            <span className="user-email">{user.email}</span>
          </div>
        )}

        <button onClick={handleLogout} className="btn-icon-logout" title="Logout">
          <LogOut size={20} />
        </button>
      </div>
    </header>
  );
}
