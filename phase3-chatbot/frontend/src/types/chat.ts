/**
 * TypeScript types for chat functionality
 */

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

export interface User {
  id: number;
  email: string;
}
