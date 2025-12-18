/**
 * Session management utilities
 *
 * Spec Reference: specs/ui/chatkit-integration.md - Session Management
 * Task: 5.5
 */

/**
 * Generate a unique session ID for the chat
 * Format: sess_{timestamp}_{random}
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
