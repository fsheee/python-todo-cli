'use client';

import { useState } from 'react';
import Link from 'next/link';
import { SignUpFormProps, RegisterInput } from '@/types';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Checkbox } from '../ui/Checkbox';
import { PasswordRequirements } from './PasswordRequirements';
import { validateEmail, validatePassword, isPasswordValid } from '@/lib/utils';

export function SignUpForm({ onSubmit, loading = false, error }: SignUpFormProps) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [errors, setErrors] = useState<{ name?: string; email?: string; password?: string }>({});

  const passwordValidation = validatePassword(password);
  const isFormValid =
    name.trim() &&
    validateEmail(email) &&
    isPasswordValid(passwordValidation) &&
    acceptTerms;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors: typeof errors = {};

    if (!name.trim()) {
      newErrors.name = 'Name is required';
    }
    if (!validateEmail(email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    if (!isPasswordValid(passwordValidation)) {
      newErrors.password = 'Password does not meet requirements';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setErrors({});
    const data: RegisterInput = { name: name.trim(), email, password };
    await onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
          {error}
        </div>
      )}

      <Input
        type="text"
        label="Name"
        placeholder="John Doe"
        value={name}
        onChange={setName}
        error={errors.name}
        required
      />

      <Input
        type="email"
        label="Email"
        placeholder="you@example.com"
        value={email}
        onChange={setEmail}
        error={errors.email}
        required
      />

      <div>
        <Input
          type="password"
          label="Password"
          placeholder="Create a password"
          value={password}
          onChange={setPassword}
          error={errors.password}
          required
        />
        <PasswordRequirements password={password} />
      </div>

      <Checkbox
        checked={acceptTerms}
        onChange={setAcceptTerms}
        label="I agree to the Terms of Service"
      />

      <Button
        type="submit"
        loading={loading}
        disabled={!isFormValid}
        className="w-full"
      >
        Create Account
      </Button>

      <p className="text-center text-sm text-gray-600">
        Already have an account?{' '}
        <Link href="/signin" className="text-primary-600 hover:text-primary-700">
          Sign in
        </Link>
      </p>
    </form>
  );
}
