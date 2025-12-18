/**
 * API client for chat endpoints using MCP tools
 *
 * Spec Reference: specs/ui/chatkit-integration.md - API Client
 * Updated to use Next.js and call MCP tools directly via backend
 */

import axios, { AxiosInstance } from 'axios';
import { useAuthStore } from '@/stores/authStore';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

/**
 * Create axios instance with auth interceptor
 */
export function createApiClient(): AxiosInstance {
  const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Add auth token to requests
  client.interceptors.request.use(
    (config) => {
      if (typeof window !== 'undefined') {
        const token = useAuthStore.getState().token;
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Handle 401 errors (logout)
  client.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401 && typeof window !== 'undefined') {
        useAuthStore.getState().logout();
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );

  return client;
}

const apiClient = createApiClient();

/**
 * Chat message type
 */
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

/**
 * Send a chat message
 */
export async function sendChatMessage(
  message: string,
  sessionId: string
): Promise<{ response: string; session_id: string; timestamp: string }> {
  const response = await apiClient.post('/chat', {
    message,
    session_id: sessionId,
  });

  return response.data;
}

/**
 * Load chat history
 */
export async function loadChatHistory(sessionId: string): Promise<ChatMessage[]> {
  try {
    const response = await apiClient.get(`/chat/history/${sessionId}`);
    return response.data.messages || [];
  } catch (error) {
    console.warn('Could not load chat history:', error);
    return [];
  }
}

/**
 * Login with Better Auth
 */
export async function login(email: string, password: string) {
  const response = await apiClient.post('/auth/login', { email, password });
  return response.data;
}
