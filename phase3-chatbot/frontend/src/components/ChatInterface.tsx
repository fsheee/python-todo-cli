/**
 * Main chat interface component for Next.js
 *
 * Spec Reference: specs/ui/chatkit-integration.md
 * Updated for Next.js + OpenAI ChatKit integration
 */

'use client';

import React, { useState, useEffect } from 'react';
import { sendChatMessage, loadChatHistory } from '@/lib/apiClient';
import { getSessionId, startNewSession } from '@/lib/sessionManager';
import { useAuthStore } from '@/stores/authStore';
import { ChatMessage } from '@/types/chat';
import { useRouter } from 'next/navigation';

export default function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const { user, logout } = useAuthStore();
  const router = useRouter();

  // Initialize session
  useEffect(() => {
    const currentSessionId = getSessionId();
    setSessionId(currentSessionId);

    // Load history
    loadChatHistory(currentSessionId)
      .then((history) => {
        if (history.length > 0) {
          setMessages(history);
        }
      })
      .catch(console.error);
  }, []);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    const content = inputValue.trim();
    if (!content) return;

    // Optimistic UI update
    const userMessage: ChatMessage = {
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await sendChatMessage(content, sessionId);

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      console.error('Failed to send message:', error);

      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: "I'm sorry, I encountered an error. Please try again.",
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    const newSessionId = startNewSession();
    setSessionId(newSessionId);
    setMessages([]);
  };

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <div className="chat-container">
      {/* Header */}
      <header className="chat-header">
        <div className="header-left">
          <h1>Todo Assistant</h1>
          {user && <span className="user-email">{user.email}</span>}
        </div>
        <div className="header-right">
          <button onClick={handleNewChat} className="btn-secondary">
            New Chat
          </button>
          <button onClick={handleLogout} className="btn-secondary">
            Logout
          </button>
        </div>
      </header>

      {/* Messages */}
      <main className="chat-main">
        <div className="messages">
          {messages.length === 0 && (
            <div className="welcome">
              <p>👋 Hello! I'm your AI todo assistant.</p>
              <p>How can I help you manage your tasks today?</p>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div key={idx} className={`message message-${msg.role}`}>
              <div className="message-content">{msg.content}</div>
              {msg.timestamp && (
                <div className="message-time">{formatTime(msg.timestamp)}</div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="message message-assistant">
              <div className="loading">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <form className="input-form" onSubmit={handleSendMessage}>
          <input
            type="text"
            className="input"
            placeholder="Ask me about your todos..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={isLoading}
          />
          <button
            type="submit"
            className="btn-send"
            disabled={isLoading || !inputValue.trim()}
          >
            Send
          </button>
        </form>
      </main>
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
  return date.toLocaleDateString();
}
