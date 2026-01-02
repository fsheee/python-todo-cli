'use client';

import { CheckboxProps } from '@/types';
import { cn } from '@/lib/utils';

export function Checkbox({
  checked,
  onChange,
  label,
  disabled = false,
  className,
}: CheckboxProps) {
  return (
    <label
      className={cn(
        'inline-flex items-center gap-2 cursor-pointer',
        disabled && 'cursor-not-allowed opacity-50',
        className
      )}
    >
      <div className="relative">
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          disabled={disabled}
          className="sr-only peer"
          role="checkbox"
          aria-checked={checked}
        />
        <div
          className={cn(
            'w-5 h-5 rounded border-2 transition-colors flex items-center justify-center',
            'peer-focus:ring-2 peer-focus:ring-primary-500 peer-focus:ring-offset-2',
            checked
              ? 'bg-primary-600 border-primary-600'
              : 'bg-white border-gray-300 hover:border-gray-400'
          )}
        >
          {checked && (
            <svg
              className="w-3 h-3 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={3}
                d="M5 13l4 4L19 7"
              />
            </svg>
          )}
        </div>
      </div>
      {label && <span className="text-sm text-gray-700">{label}</span>}
    </label>
  );
}
