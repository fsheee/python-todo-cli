/**
 * Session management utilities for Next.js
 *
 * Spec Reference: specs/ui/chatkit-integration.md - Session Management
 */

/**
 * Generate a unique session ID
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
  if (typeof window === 'undefined') return '';

  const stored = localStorage.getItem('chat_session_id');
  if (stored) return stored;

  const newSessionId = generateSessionId();
  localStorage.setItem('chat_session_id', newSessionId);
  return newSessionId;
}

/**
 * Start a new chat session
 */
export function startNewSession(): string {
  if (typeof window === 'undefined') return '';

  const newSessionId = generateSessionId();
  localStorage.setItem('chat_session_id', newSessionId);
  return newSessionId;
}

/**
 * Clear current session
 */
export function clearSession(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('chat_session_id');
  }
}
