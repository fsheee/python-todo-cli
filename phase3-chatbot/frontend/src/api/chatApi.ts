/**
 * API client for chat endpoints
 *
 * Spec Reference: specs/ui/chatkit-integration.md - API Client
 * Tasks: 5.6, 5.7, 5.8
 */

import axios, { AxiosInstance } from 'axios';
import { useAuthStore } from '../stores/authStore';
import { ChatMessage, ChatRequest, ChatResponse } from '../types/chat';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

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
      const token = useAuthStore.getState().token;
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Handle 401 errors (logout)
  client.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        useAuthStore.getState().logout();
      }
      return Promise.reject(error);
    }
  );

  return client;
}

const apiClient = createApiClient();

/**
 * Send a chat message
 */
export async function sendChatMessage(
  message: string,
  sessionId: string
): Promise<ChatResponse> {
  const response = await apiClient.post<ChatResponse>('/chat', {
    message,
    session_id: sessionId,
  });

  return response.data;
}

/**
 * Load chat history for a session (optional endpoint)
 */
export async function loadChatHistory(sessionId: string): Promise<ChatMessage[]> {
  try {
    const response = await apiClient.get<{ messages: ChatMessage[] }>(
      `/chat/history/${sessionId}`
    );
    return response.data.messages;
  } catch (error) {
    // History endpoint is optional, return empty on error
    console.warn('Could not load chat history:', error);
    return [];
  }
}
