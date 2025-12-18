/**
 * Authentication store using Zustand
 *
 * Spec Reference: specs/ui/chatkit-integration.md - Authentication Store
 * Task: 5.4
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: number;
  email: string;
}

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,

      login: (token: string, user: User) => {
        set({ token, user, isAuthenticated: true });
      },

      logout: () => {
        set({ token: null, user: null, isAuthenticated: false });
        // Clear session from localStorage
        localStorage.removeItem('chat_session_id');
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);
