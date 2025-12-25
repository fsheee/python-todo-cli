/**
 * Login page for Next.js - Modern Design
 */

'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/stores/authStore';
import { login } from '@/lib/apiClient';
import { Mail, Lock, Eye, EyeOff, ArrowLeft } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const { login: storeLogin } = useAuthStore();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const data = await login(email, password);
      storeLogin(data.access_token, data.user);

      // Brief delay before redirect for better UX
      setTimeout(() => router.push('/chat'), 500);
    } catch (err: any) {
      console.error('Login failed:', err);

      // Parse error and show specific message
      const message = err.response?.data?.detail || '';

      if (message.toLowerCase().includes('email')) {
        setError('Invalid email address');
      } else if (message.toLowerCase().includes('password')) {
        setError('Incorrect password. Please try again.');
      } else if (message.toLowerCase().includes('not found')) {
        setError('Account not found. Please check your email or sign up.');
      } else if (err.code === 'ECONNABORTED' || err.code === 'ERR_NETWORK') {
        setError('Unable to connect. Please check your internet connection.');
      } else {
        setError('Login failed. Please try again later.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-page-modern">
      {/* Animated Background */}
      <div className="login-background">
        <div className="gradient-orb login-orb-1"></div>
        <div className="gradient-orb login-orb-2"></div>
      </div>

      {/* Login Card */}
      <div className="login-card-modern">
        {/* Header */}
        <div className="login-header">
          <div className="logo-container">
            <span className="logo-icon">✨</span>
            <h1 className="login-title">Todo Assistant</h1>
          </div>
          <p className="login-subtitle">Welcome back! Sign in to continue</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="login-form">
          {/* Email Field */}
          <div className="input-group">
            <label htmlFor="email" className="input-label">
              Email Address
            </label>
            <div className="input-wrapper">
              <Mail size={20} className="input-icon" />
              <input
                type="email"
                id="email"
                className="input-field"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={isLoading}
                placeholder="your@email.com"
                autoComplete="email"
                aria-label="Email address"
                aria-required="true"
              />
            </div>
          </div>

          {/* Password Field */}
          <div className="input-group">
            <label htmlFor="password" className="input-label">
              Password
            </label>
            <div className="input-wrapper">
              <Lock size={20} className="input-icon" />
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                className="input-field"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={isLoading}
                placeholder="••••••••"
                autoComplete="current-password"
                aria-label="Password"
                aria-required="true"
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? "Hide password" : "Show password"}
                tabIndex={-1}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="error-message" role="alert" aria-live="polite">
              <span className="error-icon" aria-hidden="true">⚠️</span>
              {error}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="btn-login"
          >
            {isLoading ? (
              <>
                <span className="loading-spinner"></span>
                Signing in...
              </>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        {/* Footer Links */}
        <div className="login-footer">
          <Link href="/" className="link-back">
            <ArrowLeft size={16} />
            Back to Home
          </Link>

          {/* Uncomment if signup is available */}
          {/* <p className="signup-prompt">
            Don't have an account?{' '}
            <Link href="/signup" className="link-signup">
              Sign up free
            </Link>
          </p> */}
        </div>
      </div>
    </div>
  );
}
