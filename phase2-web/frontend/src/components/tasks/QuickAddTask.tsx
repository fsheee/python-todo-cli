'use client';

import { useState, useRef, KeyboardEvent } from 'react';
import { QuickAddTaskProps } from '@/types';
import { cn } from '@/lib/utils';

export function QuickAddTask({
  onAdd,
  placeholder = 'Add a task...',
  disabled = false,
}: QuickAddTaskProps) {
  const [title, setTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async () => {
    const trimmedTitle = title.trim();
    if (!trimmedTitle || loading) return;

    setLoading(true);
    try {
      await onAdd(trimmedTitle);
      setTitle('');
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    } else if (e.key === 'Escape') {
      setTitle('');
      inputRef.current?.blur();
    }
  };

  return (
    <div
      className={cn(
        'flex items-center gap-3 p-4 bg-white rounded-lg border border-gray-200',
        'focus-within:border-primary-500 focus-within:ring-2 focus-within:ring-primary-500/20',
        'transition-all'
      )}
    >
      <svg
        className="w-5 h-5 text-gray-400 flex-shrink-0"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 4v16m8-8H4"
        />
      </svg>

      <input
        ref={inputRef}
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled || loading}
        className="flex-1 bg-transparent outline-none text-gray-900 placeholder-gray-400 disabled:cursor-not-allowed"
      />

      {loading && (
        <svg
          className="animate-spin w-5 h-5 text-primary-600"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}
    </div>
  );
}
