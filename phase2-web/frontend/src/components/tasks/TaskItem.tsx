'use client';

import { useState } from 'react';
import { TaskItemProps } from '@/types';
import { Checkbox } from '../ui/Checkbox';
import { formatDate } from '@/lib/utils';
import { cn } from '@/lib/utils';

export function TaskItem({ task, onToggle, onEdit, onDelete }: TaskItemProps) {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div
      className={cn(
        'flex items-center gap-3 p-4 bg-white rounded-lg border border-gray-200',
        'hover:border-gray-300 transition-colors group'
      )}
    >
      <Checkbox
        checked={task.completed}
        onChange={() => onToggle(task.id)}
      />

      <div className="flex-1 min-w-0">
        <button
          onClick={() => onEdit(task.id)}
          className={cn(
            'text-left w-full font-medium text-gray-900 truncate',
            task.completed && 'line-through text-gray-500'
          )}
        >
          {task.title}
        </button>
        <p className="text-xs text-gray-500 mt-0.5">
          Created: {formatDate(task.created_at)}
        </p>
      </div>

      <div className="relative">
        <button
          onClick={() => setMenuOpen(!menuOpen)}
          className="p-1 rounded text-gray-400 hover:text-gray-600 hover:bg-gray-100 opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"
            />
          </svg>
        </button>

        {menuOpen && (
          <>
            <div
              className="fixed inset-0 z-10"
              onClick={() => setMenuOpen(false)}
            />
            <div className="absolute right-0 top-full mt-1 w-32 bg-white rounded-lg shadow-lg border border-gray-200 z-20 py-1">
              <button
                onClick={() => {
                  setMenuOpen(false);
                  onEdit(task.id);
                }}
                className="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-100"
              >
                Edit
              </button>
              <button
                onClick={() => {
                  setMenuOpen(false);
                  onDelete(task.id);
                }}
                className="w-full px-3 py-2 text-left text-sm text-red-600 hover:bg-red-50"
              >
                Delete
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
