/**
 * Signup page for Next.js - Modern Design
 */

'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/stores/authStore';
import axios from 'axios';
import { Mail, Lock, Eye, EyeOff, ArrowLeft, User } from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export default function SignupPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const { login: storeLogin } = useAuthStore();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/auth/signup`, {
        email,
        password,
        name: name || undefined,
      });

      if (response.data.access_token) {
        storeLogin(response.data.access_token, response.data.user);

        // Brief delay before redirect for better UX
        setTimeout(() => router.push('/chat'), 500);
      }
    } catch (err: any) {
      console.error('Signup failed:', err);

      const message = err.response?.data?.detail || '';

      if (message.toLowerCase().includes('already registered') || message.toLowerCase().includes('exists')) {
        setError('Email already registered. Please login instead.');
      } else if (message.toLowerCase().includes('email')) {
        setError('Invalid email address');
      } else if (message.toLowerCase().includes('password')) {
        setError('Password does not meet requirements');
      } else if (err.code === 'ECONNABORTED' || err.code === 'ERR_NETWORK') {
        setError('Unable to connect. Please check your internet connection.');
      } else {
        setError('Signup failed. Please try again later.');
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

      {/* Signup Card */}
      <div className="login-card-modern">
        {/* Header */}
        <div className="login-header">
          <div className="logo-container">
            <span className="logo-icon">✨</span>
            <h1 className="login-title">Todo Assistant</h1>
          </div>
          <p className="login-subtitle">Create your account to get started</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="login-form">
          {/* Name Field */}
          <div className="input-group">
            <label htmlFor="name" className="input-label">
              Full Name (Optional)
            </label>
            <div className="input-wrapper">
              <User size={20} className="input-icon" />
              <input
                type="text"
                id="name"
                className="input-field"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={isLoading}
                placeholder="John Doe"
                autoComplete="name"
                aria-label="Full name"
              />
            </div>
          </div>

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
                autoComplete="new-password"
                aria-label="Password"
                aria-required="true"
                minLength={8}
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
            <p className="input-hint">Minimum 8 characters</p>
          </div>

          {/* Confirm Password Field */}
          <div className="input-group">
            <label htmlFor="confirmPassword" className="input-label">
              Confirm Password
            </label>
            <div className="input-wrapper">
              <Lock size={20} className="input-icon" />
              <input
                type={showConfirmPassword ? 'text' : 'password'}
                id="confirmPassword"
                className="input-field"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                disabled={isLoading}
                placeholder="••••••••"
                autoComplete="new-password"
                aria-label="Confirm password"
                aria-required="true"
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                aria-label={showConfirmPassword ? "Hide password" : "Show password"}
                tabIndex={-1}
              >
                {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
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
                Creating account...
              </>
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        {/* Footer Links */}
        <div className="login-footer">
          <Link href="/" className="link-back">
            <ArrowLeft size={16} />
            Back to Home
          </Link>

          <p className="signup-prompt">
            Already have an account?{' '}
            <Link href="/login" className="link-signup">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
