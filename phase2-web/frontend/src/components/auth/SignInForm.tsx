'use client';

import { useState } from 'react';
import Link from 'next/link';
import { SignInFormProps } from '@/types';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Checkbox } from '../ui/Checkbox';
import { validateEmail } from '@/lib/utils';

export function SignInForm({
  onSubmit,
  onForgotPassword,
  loading = false,
  error,
}: SignInFormProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [emailError, setEmailError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setEmailError('');

    if (!validateEmail(email)) {
      setEmailError('Please enter a valid email address');
      return;
    }

    await onSubmit(email, password);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
          {error}
        </div>
      )}

      <Input
        type="email"
        label="Email"
        placeholder="you@example.com"
        value={email}
        onChange={setEmail}
        error={emailError}
        required
      />

      <Input
        type="password"
        label="Password"
        placeholder="Enter your password"
        value={password}
        onChange={setPassword}
        required
      />

      <div className="flex items-center justify-between">
        <Checkbox
          checked={rememberMe}
          onChange={setRememberMe}
          label="Remember me"
        />
        <button
          type="button"
          onClick={onForgotPassword}
          className="text-sm text-primary-600 hover:text-primary-700"
        >
          Forgot password?
        </button>
      </div>

      <Button
        type="submit"
        loading={loading}
        disabled={!email || !password}
        className="w-full"
      >
        Sign In
      </Button>

      <p className="text-center text-sm text-gray-600">
        Don&apos;t have an account?{' '}
        <Link href="/signup" className="text-primary-600 hover:text-primary-700">
          Sign up
        </Link>
      </p>
    </form>
  );
}
