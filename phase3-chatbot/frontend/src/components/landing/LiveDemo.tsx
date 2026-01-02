/**
 * Live ChatKit demo component for landing page
 * Allows visitors to try the chatbot without signing up
 */

'use client';

import { useState } from 'react';
import { getDemoResponse, getInitialDemoMessages, DemoMessage } from '@/lib/demoResponses';
import Link from 'next/link';

export default function LiveDemo() {
  const [demoMessages, setDemoMessages] = useState<DemoMessage[]>(getInitialDemoMessages());
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleDemoMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    const content = inputValue.trim();
    if (!content) return;

    // Add user message
    const userMsg: DemoMessage = {
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };

    setDemoMessages((prev) => [...prev, userMsg]);
    setInputValue('');
    setIsLoading(true);

    // Simulate AI response delay
    setTimeout(() => {
      const response = getDemoResponse(content);

      const aiMsg: DemoMessage = {
        role: 'assistant',
        content: response,
        timestamp: new Date().toISOString(),
      };

      setDemoMessages((prev) => [...prev, aiMsg]);
      setIsLoading(false);
    }, 1000);
  };

  const handleSuggestedPrompt = (prompt: string) => {
    setInputValue(prompt);
  };

  return (
    <section id="demo-section" className="demo-section">
      <div className="section-container">
        <div className="section-header fade-in">
          <h2 className="section-title">See It In Action</h2>
          <p className="section-subtitle">
            Try chatting with the AI (demo mode - no signup needed!)
          </p>
        </div>

        <div className="demo-chat-container">
          {/* Simple Chat UI (ChatKit alternative for demo) */}
          <div className="demo-chat">
            <div className="demo-messages">
              {demoMessages.map((msg, idx) => (
                <div key={idx} className={`demo-message demo-${msg.role}`}>
                  <div className="message-content">{msg.content}</div>
                </div>
              ))}

              {isLoading && (
                <div className="demo-message demo-assistant">
                  <div className="loading-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              )}
            </div>

            {/* Suggested Prompts */}
            <div className="demo-suggestions">
              {['Show my tasks', 'Add buy milk', 'Help'].map((prompt) => (
                <button
                  key={prompt}
                  className="suggestion-chip"
                  onClick={() => handleSuggestedPrompt(prompt)}
                >
                  {prompt}
                </button>
              ))}
            </div>

            {/* Input Form */}
            <form className="demo-input-form" onSubmit={handleDemoMessage}>
              <input
                type="text"
                className="demo-input"
                placeholder="Try: 'Show my tasks' or 'Add buy milk'"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                disabled={isLoading}
              />
              <button
                type="submit"
                className="demo-send-btn"
                disabled={isLoading || !inputValue.trim()}
              >
                Send
              </button>
            </form>
          </div>

          {/* CTA */}
          <div className="demo-cta">
            <p className="demo-note">
              Like what you see? This is just a demo with sample data.
            </p>
            <Link href="/login">
              <button className="btn-demo-cta">
                Sign Up to Save Your Todos
              </button>
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
