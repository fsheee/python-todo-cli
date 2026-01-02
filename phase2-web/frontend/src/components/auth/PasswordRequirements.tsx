'use client';

import { PasswordRequirementsProps } from '@/types';
import { validatePassword } from '@/lib/utils';
import { cn } from '@/lib/utils';

export function PasswordRequirements({ password }: PasswordRequirementsProps) {
  const validation = validatePassword(password);

  const requirements = [
    { key: 'minLength', label: 'At least 8 characters', met: validation.minLength },
    { key: 'hasUppercase', label: 'One uppercase letter', met: validation.hasUppercase },
    { key: 'hasLowercase', label: 'One lowercase letter', met: validation.hasLowercase },
    { key: 'hasNumber', label: 'One number', met: validation.hasNumber },
  ];

  return (
    <div className="mt-2 space-y-1">
      <p className="text-xs text-gray-500">Password requirements:</p>
      <div className="grid grid-cols-2 gap-1">
        {requirements.map((req) => (
          <div
            key={req.key}
            className={cn(
              'flex items-center gap-1.5 text-xs',
              req.met ? 'text-green-600' : 'text-gray-400'
            )}
          >
            {req.met ? (
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            )}
            {req.label}
          </div>
        ))}
      </div>
    </div>
  );
}
