# ChatKit Integration Specification

## 🎯 Overview

This document specifies the frontend implementation using OpenAI ChatKit for the conversational todo management interface. ChatKit provides the chat UI components while integrating with our FastAPI backend.

---

## 🏗 Architecture

### Component Structure

```
┌─────────────────────────────────────────────────────────┐
│                  React Application                       │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │          App Component                         │    │
│  │  - Authentication State                        │    │
│  │  - Session Management                          │    │
│  │  - Route Handling                              │    │
│  └──────────────────┬─────────────────────────────┘    │
│                     │                                    │
│  ┌──────────────────▼─────────────────────────────┐    │
│  │      TodoChatInterface Component               │    │
│  │  - Chat State Management                       │    │
│  │  - API Communication                           │    │
│  │  - Session ID Management                       │    │
│  └──────────────────┬─────────────────────────────┘    │
│                     │                                    │
│  ┌──────────────────▼─────────────────────────────┐    │
│  │        OpenAI ChatKit Component                │    │
│  │  - Message Display                             │    │
│  │  - Input Handling                              │    │
│  │  - Typing Indicators                           │    │
│  │  - Message Formatting                          │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
└───────────────────────────┬──────────────────────────────┘
                            │
                            │ HTTP POST /chat
                            │ Authorization: Bearer {token}
                            ▼
┌─────────────────────────────────────────────────────────┐
│               FastAPI Backend                            │
│  POST /chat                                              │
│  - Validates JWT                                         │
│  - Loads history                                         │
│  - Calls AI agent                                        │
│  - Saves messages                                        │
│  - Returns response                                      │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Dependencies

### Package Installation

```json
{
  "name": "todo-chatbot-ui",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@openai/chatkit": "^1.0.0",
    "axios": "^1.6.0",
    "react-router-dom": "^6.20.0",
    "zustand": "^4.4.7",
    "@radix-ui/react-toast": "^1.1.5"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0"
  }
}
```

### Installation

```bash
npm install @openai/chatkit axios zustand
```

---

## 🎨 Component Implementation

### 1. Main App Component

**File:** `src/App.tsx`

```typescript
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './stores/authStore';
import LoginPage from './pages/LoginPage';
import TodoChatInterface from './components/TodoChatInterface';

function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <BrowserRouter>
      <div className="app">
        <Routes>
          <Route
            path="/login"
            element={!isAuthenticated ? <LoginPage /> : <Navigate to="/chat" />}
          />
          <Route
            path="/chat"
            element={isAuthenticated ? <TodoChatInterface /> : <Navigate to="/login" />}
          />
          <Route path="/" element={<Navigate to="/chat" />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
```

### 2. Authentication Store

**File:** `src/stores/authStore.ts`

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  token: string | null;
  user: { id: number; email: string } | null;
  isAuthenticated: boolean;
  login: (token: string, user: { id: number; email: string }) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,

      login: (token, user) => {
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
```

### 3. Session Management

**File:** `src/utils/sessionManager.ts`

```typescript
/**
 * Generate a unique session ID for the chat
 */
export function generateSessionId(): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 10);
  return `sess_${timestamp}_${random}`;
}

/**
 * Get or create session ID from localStorage
 */
export function getSessionId(): string {
  const stored = localStorage.getItem('chat_session_id');

  if (stored) {
    return stored;
  }

  const newSessionId = generateSessionId();
  localStorage.setItem('chat_session_id', newSessionId);
  return newSessionId;
}

/**
 * Start a new chat session
 */
export function startNewSession(): string {
  const newSessionId = generateSessionId();
  localStorage.setItem('chat_session_id', newSessionId);
  return newSessionId;
}

/**
 * Clear current session
 */
export function clearSession(): void {
  localStorage.removeItem('chat_session_id');
}
```

### 4. API Client

**File:** `src/api/chatApi.ts`

```typescript
import axios, { AxiosInstance } from 'axios';
import { useAuthStore } from '../stores/authStore';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
 * Chat message type
 */
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

/**
 * Chat request payload
 */
export interface ChatRequest {
  message: string;
  session_id: string;
}

/**
 * Chat response
 */
export interface ChatResponse {
  response: string;
  session_id: string;
  timestamp: string;
}

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
 * Load chat history for a session
 */
export async function loadChatHistory(sessionId: string): Promise<ChatMessage[]> {
  const response = await apiClient.get<{ messages: ChatMessage[] }>(
    `/chat/history/${sessionId}`
  );

  return response.data.messages;
}
```

### 5. Main Chat Interface Component

**File:** `src/components/TodoChatInterface.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import { ChatKit } from '@openai/chatkit';
import { sendChatMessage, loadChatHistory, ChatMessage } from '../api/chatApi';
import { getSessionId, startNewSession } from '../utils/sessionManager';
import { useAuthStore } from '../stores/authStore';
import { toast } from '../components/Toast';

interface TodoChatInterfaceProps {}

const TodoChatInterface: React.FC<TodoChatInterfaceProps> = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const { user, logout } = useAuthStore();

  // Initialize session and load history
  useEffect(() => {
    const currentSessionId = getSessionId();
    setSessionId(currentSessionId);

    // Load chat history
    loadChatHistory(currentSessionId)
      .then((history) => {
        setMessages(history);
      })
      .catch((error) => {
        console.error('Failed to load chat history:', error);
        toast.error('Failed to load chat history');
      });
  }, []);

  /**
   * Handle user sending a message
   */
  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;

    // Add user message to UI immediately
    const userMessage: ChatMessage = {
      role: 'user',
      content: content.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Send to backend
      const response = await sendChatMessage(content.trim(), sessionId);

      // Add assistant response to UI
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      console.error('Failed to send message:', error);

      // Show error message
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: "I'm sorry, I encountered an error. Please try again.",
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, errorMessage]);
      toast.error('Failed to send message');
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Start a new conversation
   */
  const handleNewConversation = () => {
    const newSessionId = startNewSession();
    setSessionId(newSessionId);
    setMessages([]);
    toast.success('Started new conversation');
  };

  /**
   * Handle logout
   */
  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully');
  };

  return (
    <div className="todo-chat-container">
      {/* Header */}
      <header className="chat-header">
        <div className="header-left">
          <h1>Todo Assistant</h1>
          {user && <span className="user-email">{user.email}</span>}
        </div>
        <div className="header-right">
          <button onClick={handleNewConversation} className="btn-secondary">
            New Chat
          </button>
          <button onClick={handleLogout} className="btn-secondary">
            Logout
          </button>
        </div>
      </header>

      {/* Chat Interface */}
      <main className="chat-main">
        <ChatKit
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          placeholder="Ask me about your todos..."
          welcomeMessage="Hello! I'm your AI todo assistant. How can I help you today?"
          theme="light"
          showTimestamps={true}
          enableMarkdown={true}
        />
      </main>
    </div>
  );
};

export default TodoChatInterface;
```

### 6. ChatKit Configuration

**File:** `src/components/ChatKitWrapper.tsx`

```typescript
import React from 'react';
import { ChatKit, ChatKitProps } from '@openai/chatkit';
import '@openai/chatkit/dist/index.css';
import './ChatKitWrapper.css';

interface ChatKitWrapperProps extends Partial<ChatKitProps> {
  messages: Array<{ role: string; content: string; timestamp?: string }>;
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
}

/**
 * Wrapper component for OpenAI ChatKit with custom styling
 */
const ChatKitWrapper: React.FC<ChatKitWrapperProps> = ({
  messages,
  onSendMessage,
  isLoading = false,
  placeholder = "Type a message...",
  welcomeMessage,
  ...props
}) => {
  return (
    <div className="chatkit-wrapper">
      <ChatKit
        messages={messages}
        onSendMessage={onSendMessage}
        isLoading={isLoading}
        placeholder={placeholder}
        welcomeMessage={welcomeMessage}
        theme="light"
        showTimestamps={true}
        enableMarkdown={true}
        renderMessage={(message) => (
          <div className={`message message-${message.role}`}>
            <div className="message-content">
              {formatMessageContent(message.content)}
            </div>
            {message.timestamp && (
              <div className="message-timestamp">
                {formatTimestamp(message.timestamp)}
              </div>
            )}
          </div>
        )}
        {...props}
      />
    </div>
  );
};

/**
 * Format message content with markdown
 */
function formatMessageContent(content: string): React.ReactNode {
  // Basic markdown formatting
  // In production, use a proper markdown library like react-markdown

  // Convert **bold** to <strong>
  let formatted = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

  // Convert *italic* to <em>
  formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');

  // Convert `code` to <code>
  formatted = formatted.replace(/`(.*?)`/g, '<code>$1</code>');

  // Convert line breaks
  formatted = formatted.replace(/\n/g, '<br/>');

  return <div dangerouslySetInnerHTML={{ __html: formatted }} />;
}

/**
 * Format timestamp
 */
function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;

  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;

  return date.toLocaleDateString();
}

export default ChatKitWrapper;
```

---

## 🎨 Styling

### Main Styles

**File:** `src/styles/TodoChatInterface.css`

```css
.todo-chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f5f5;
}

/* Header */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #fff;
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.header-left h1 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
}

.user-email {
  display: block;
  font-size: 0.875rem;
  color: #666;
  margin-top: 0.25rem;
}

.header-right {
  display: flex;
  gap: 0.5rem;
}

/* Buttons */
.btn-secondary {
  padding: 0.5rem 1rem;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background-color: #f5f5f5;
  border-color: #ccc;
}

/* Chat Main Area */
.chat-main {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* ChatKit Wrapper */
.chatkit-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* Message Styles */
.message {
  margin-bottom: 1rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  max-width: 70%;
}

.message-user {
  background-color: #007bff;
  color: #fff;
  align-self: flex-end;
  margin-left: auto;
}

.message-assistant {
  background-color: #fff;
  color: #333;
  border: 1px solid #e0e0e0;
  align-self: flex-start;
}

.message-system {
  background-color: #f8f9fa;
  color: #666;
  text-align: center;
  align-self: center;
  max-width: 80%;
  font-size: 0.875rem;
}

.message-content {
  line-height: 1.5;
  word-wrap: break-word;
}

.message-content strong {
  font-weight: 600;
}

.message-content code {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 0.125rem 0.25rem;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.875em;
}

.message-timestamp {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 0.25rem;
}

.message-assistant .message-timestamp {
  color: #999;
}

/* Loading Indicator */
.loading-indicator {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
}

.loading-dots {
  display: flex;
  gap: 0.25rem;
}

.loading-dot {
  width: 8px;
  height: 8px;
  background-color: #999;
  border-radius: 50%;
  animation: pulse 1.4s infinite ease-in-out both;
}

.loading-dot:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes pulse {
  0%, 80%, 100% {
    opacity: 0.3;
  }
  40% {
    opacity: 1;
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .chat-header {
    padding: 0.75rem 1rem;
  }

  .header-left h1 {
    font-size: 1.25rem;
  }

  .message {
    max-width: 85%;
  }

  .header-right {
    flex-direction: column;
  }
}
```

---

## 🔄 State Management

### Chat State Hook

**File:** `src/hooks/useChatState.ts`

```typescript
import { useState, useCallback } from 'react';
import { ChatMessage } from '../api/chatApi';

interface UseChatStateReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  addMessage: (message: ChatMessage) => void;
  clearMessages: () => void;
  setLoading: (loading: boolean) => void;
}

export function useChatState(): UseChatStateReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const addMessage = useCallback((message: ChatMessage) => {
    setMessages((prev) => [...prev, message]);
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const setLoading = useCallback((loading: boolean) => {
    setIsLoading(loading);
  }, []);

  return {
    messages,
    isLoading,
    addMessage,
    clearMessages,
    setLoading,
  };
}
```

---

## 🔐 Authentication Flow

### Login Page

**File:** `src/pages/LoginPage.tsx`

```typescript
import React, { useState } from 'react';
import axios from 'axios';
import { useAuthStore } from '../stores/authStore';
import { useNavigate } from 'react-router-dom';
import { toast } from '../components/Toast';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Call Better Auth login endpoint
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/auth/login`,
        { email, password }
      );

      const { access_token, user } = response.data;

      // Save to auth store
      login(access_token, user);

      // Navigate to chat
      navigate('/chat');
      toast.success('Logged in successfully');
    } catch (error: any) {
      console.error('Login failed:', error);
      toast.error(error.response?.data?.detail || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>Todo Assistant</h1>
        <p>Sign in to manage your todos with AI</p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>

          <button type="submit" disabled={isLoading} className="btn-primary">
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;
```

---

## 🧪 Testing

### Component Tests

**File:** `src/components/__tests__/TodoChatInterface.test.tsx`

```typescript
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';
import TodoChatInterface from '../TodoChatInterface';
import * as chatApi from '../../api/chatApi';

vi.mock('../../api/chatApi');

describe('TodoChatInterface', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  test('renders chat interface', () => {
    render(<TodoChatInterface />);
    expect(screen.getByText('Todo Assistant')).toBeInTheDocument();
  });

  test('loads chat history on mount', async () => {
    const mockHistory = [
      { role: 'user', content: 'Hello', timestamp: '2025-12-18T10:00:00Z' },
      { role: 'assistant', content: 'Hi there!', timestamp: '2025-12-18T10:00:01Z' },
    ];

    vi.spyOn(chatApi, 'loadChatHistory').mockResolvedValue(mockHistory);

    render(<TodoChatInterface />);

    await waitFor(() => {
      expect(screen.getByText('Hello')).toBeInTheDocument();
      expect(screen.getByText('Hi there!')).toBeInTheDocument();
    });
  });

  test('sends message and displays response', async () => {
    vi.spyOn(chatApi, 'sendChatMessage').mockResolvedValue({
      response: "I've created 'Buy milk'",
      session_id: 'sess_123',
      timestamp: '2025-12-18T10:00:00Z',
    });

    render(<TodoChatInterface />);

    const input = screen.getByPlaceholderText('Ask me about your todos...');
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'Add buy milk' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('Add buy milk')).toBeInTheDocument();
      expect(screen.getByText("I've created 'Buy milk'")).toBeInTheDocument();
    });
  });

  test('starts new conversation', () => {
    render(<TodoChatInterface />);

    const newChatButton = screen.getByText('New Chat');
    fireEvent.click(newChatButton);

    // Should clear messages and generate new session ID
    const sessionId = localStorage.getItem('chat_session_id');
    expect(sessionId).toMatch(/^sess_\d+_[a-z0-9]+$/);
  });
});
```

---

## 📱 Responsive Design

### Mobile Optimizations

```css
/* Mobile-specific styles */
@media (max-width: 768px) {
  .todo-chat-container {
    font-size: 14px;
  }

  .chat-header {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }

  .header-right {
    justify-content: space-between;
  }

  .message {
    max-width: 90%;
    font-size: 0.875rem;
  }

  /* Adjust input area for mobile keyboards */
  .chat-input-container {
    padding-bottom: env(safe-area-inset-bottom);
  }
}

/* Tablet styles */
@media (min-width: 769px) and (max-width: 1024px) {
  .message {
    max-width: 75%;
  }
}
```

---

## 🚀 Deployment

### Environment Variables

**File:** `.env.production`

```bash
VITE_API_URL=https://api.yourdomain.com
VITE_APP_NAME=Todo Assistant
VITE_ENABLE_ANALYTICS=true
```

### Build Configuration

**File:** `vite.config.ts`

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          chatkit: ['@openai/chatkit'],
        },
      },
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
});
```

### Build Commands

```bash
# Development
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Type check
npm run type-check

# Lint
npm run lint
```

---

## 📋 Implementation Checklist

- [ ] Install OpenAI ChatKit and dependencies
- [ ] Set up authentication store with Zustand
- [ ] Implement session management utilities
- [ ] Create API client with interceptors
- [ ] Build main TodoChatInterface component
- [ ] Integrate ChatKit component
- [ ] Implement message formatting
- [ ] Add loading states and error handling
- [ ] Create login page with Better Auth integration
- [ ] Style components for desktop and mobile
- [ ] Add toast notifications
- [ ] Implement new conversation feature
- [ ] Add logout functionality
- [ ] Write component tests
- [ ] Set up environment variables
- [ ] Configure build process
- [ ] Test responsive design
- [ ] Deploy to production

---

## 🔗 Related Specifications

- [../features/chatbot.md](../features/chatbot.md) - Chatbot features
- [../agents/todo-agent.md](../agents/todo-agent.md) - AI agent behavior
- [../api/mcp-tools.md](../api/mcp-tools.md) - Backend API
- [../database/chat-history.md](../database/chat-history.md) - Chat persistence
- [../../CLAUDE.md](../../CLAUDE.md) - Project constitution

---

**Status:** Draft - Ready for Review
**Last Updated:** 2025-12-18
