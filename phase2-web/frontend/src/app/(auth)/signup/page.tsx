'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { SignUpForm } from '@/components/auth/SignUpForm';
import { useAuth } from '@/lib/auth-context';
import { useToast } from '@/lib/toast-context';
import { RegisterInput, ApiError } from '@/types';

export default function SignUpPage() {
  const router = useRouter();
  const { signUp } = useAuth();
  const { showToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (data: RegisterInput) => {
    setLoading(true);
    setError('');

    try {
      await signUp(data);
      showToast('success', 'Account created successfully');
      router.push('/dashboard');
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.detail || 'Failed to create account');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="text-center mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">Create an account</h1>
        <p className="text-sm text-gray-600 mt-1">Start organizing your tasks</p>
      </div>
      <SignUpForm onSubmit={handleSubmit} loading={loading} error={error} />
    </>
  );
}
