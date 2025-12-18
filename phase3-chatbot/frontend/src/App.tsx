/**
 * Main App component with routing
 *
 * Spec Reference: specs/ui/chatkit-integration.md - Main App Component
 * Task: 5.10
 */

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
