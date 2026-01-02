'use client';

import { useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { SignInForm } from '@/components/auth/SignInForm';
import { useAuth } from '@/lib/auth-context';
import { useToast } from '@/lib/toast-context';
import { ApiError } from '@/types';

function SignInContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { signIn } = useAuth();
  const { showToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const returnUrl = searchParams.get('returnUrl') || '/dashboard';

  const handleSubmit = async (email: string, password: string) => {
    setLoading(true);
    setError('');

    try {
      await signIn(email, password);
      showToast('success', 'Signed in successfully');
      router.push(returnUrl);
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.detail || 'Failed to sign in');
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = () => {
    router.push('/forgot-password');
  };

  return (
    <>
      <div className="text-center mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">Welcome back</h1>
        <p className="text-sm text-gray-600 mt-1">Sign in to your account</p>
      </div>
      <SignInForm
        onSubmit={handleSubmit}
        onForgotPassword={handleForgotPassword}
        loading={loading}
        error={error}
      />
    </>
  );
}

export default function SignInPage() {
  return (
    <Suspense fallback={<div className="text-center">Loading...</div>}>
      <SignInContent />
    </Suspense>
  );
}
