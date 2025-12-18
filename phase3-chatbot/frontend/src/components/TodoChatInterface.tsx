/**
 * Main chat interface component
 *
 * Spec Reference: specs/ui/chatkit-integration.md - Main Chat Interface
 * Tasks: 5.11, 5.12
 */

import React, { useState, useEffect } from 'react';
import { sendChatMessage, loadChatHistory } from '../api/chatApi';
import { getSessionId, startNewSession } from '../utils/sessionManager';
import { useAuthStore } from '../stores/authStore';
import { ChatMessage } from '../types/chat';
import '../styles/TodoChatInterface.css';

const TodoChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const { user, logout } = useAuthStore();

  // Initialize session and load history
  useEffect(() => {
    const currentSessionId = getSessionId();
    setSessionId(currentSessionId);

    // Load chat history (optional)
    loadChatHistory(currentSessionId)
      .then((history) => {
        if (history.length > 0) {
          setMessages(history);
        }
      })
      .catch((error) => {
        console.error('Failed to load chat history:', error);
      });
  }, []);

  /**
   * Handle user sending a message
   */
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    const content = inputValue.trim();
    if (!content) return;

    // Add user message to UI immediately
    const userMessage: ChatMessage = {
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Send to backend
      const response = await sendChatMessage(content, sessionId);

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
  };

  /**
   * Handle logout
   */
  const handleLogout = () => {
    logout();
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

      {/* Chat Area */}
      <main className="chat-main">
        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message">
              <p>👋 Hello! I'm your AI todo assistant.</p>
              <p>How can I help you today?</p>
            </div>
          )}

          {messages.map((msg, index) => (
            <div key={index} className={`message message-${msg.role}`}>
              <div className="message-content">{msg.content}</div>
              {msg.timestamp && (
                <div className="message-timestamp">
                  {formatTimestamp(msg.timestamp)}
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="message message-assistant">
              <div className="loading-dots">
                <span className="loading-dot"></span>
                <span className="loading-dot"></span>
                <span className="loading-dot"></span>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <form className="chat-input-form" onSubmit={handleSendMessage}>
          <input
            type="text"
            className="chat-input"
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
};

/**
 * Format timestamp for display
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

export default TodoChatInterface;
