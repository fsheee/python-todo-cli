'use client';

import { useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { PasswordRequirements } from '@/components/auth/PasswordRequirements';
import { validatePassword, isPasswordValid } from '@/lib/utils';
import { useToast } from '@/lib/toast-context';

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { showToast } = useToast();
  const token = searchParams.get('token');

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const passwordValidation = validatePassword(password);
  const passwordsMatch = password === confirmPassword;
  const isFormValid = isPasswordValid(passwordValidation) && passwordsMatch && confirmPassword;

  if (!token) {
    return (
      <div className="text-center">
        <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg
            className="w-6 h-6 text-red-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </div>
        <h1 className="text-2xl font-semibold text-gray-900 mb-2">Invalid reset link</h1>
        <p className="text-sm text-gray-600 mb-6">
          This reset link is invalid or has expired.
        </p>
        <Link
          href="/forgot-password"
          className="text-primary-600 hover:text-primary-700 text-sm"
        >
          Request a new reset link
        </Link>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!passwordsMatch) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      // API call would go here
      // await api.resetPassword({ token, password });
      showToast('success', 'Password reset successfully');
      router.push('/signin');
    } catch {
      setError('Failed to reset password. The link may have expired.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="text-center mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">Create new password</h1>
        <p className="text-sm text-gray-600 mt-1">Enter your new password below</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
            {error}
          </div>
        )}

        <div>
          <Input
            type="password"
            label="New Password"
            placeholder="Enter new password"
            value={password}
            onChange={setPassword}
            required
          />
          <PasswordRequirements password={password} />
        </div>

        <Input
          type="password"
          label="Confirm Password"
          placeholder="Confirm new password"
          value={confirmPassword}
          onChange={setConfirmPassword}
          error={confirmPassword && !passwordsMatch ? 'Passwords do not match' : undefined}
          required
        />

        <Button type="submit" loading={loading} disabled={!isFormValid} className="w-full">
          Reset Password
        </Button>
      </form>
    </>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div className="text-center">Loading...</div>}>
      <ResetPasswordForm />
    </Suspense>
  );
}
