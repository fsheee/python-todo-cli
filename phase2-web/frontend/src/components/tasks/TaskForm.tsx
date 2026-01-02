'use client';

import { useState } from 'react';
import { TaskFormProps, TaskCreateInput } from '@/types';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { validateTaskTitle, validateTaskDescription } from '@/lib/utils';

export function TaskForm({
  mode,
  initialData,
  onSubmit,
  onCancel,
  loading = false,
}: TaskFormProps) {
  const [title, setTitle] = useState(initialData?.title || '');
  const [description, setDescription] = useState(initialData?.description || '');
  const [errors, setErrors] = useState<{ title?: string; description?: string }>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const titleError = validateTaskTitle(title);
    const descriptionError = validateTaskDescription(description);

    if (titleError || descriptionError) {
      setErrors({
        title: titleError || undefined,
        description: descriptionError || undefined,
      });
      return;
    }

    setErrors({});
    const data: TaskCreateInput = {
      title: title.trim(),
      description: description.trim() || undefined,
    };
    await onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        type="text"
        label="Title"
        placeholder="What needs to be done?"
        value={title}
        onChange={setTitle}
        error={errors.title}
        required
      />

      <div className="flex flex-col gap-1.5">
        <label className="text-sm font-medium text-gray-700">
          Description (optional)
        </label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Add more details..."
          rows={4}
          className="w-full px-3 py-2 rounded-lg border border-gray-300 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
        />
        {errors.description && (
          <p className="text-sm text-red-500">{errors.description}</p>
        )}
        <p className="text-xs text-gray-500 text-right">
          {description.length}/2000
        </p>
      </div>

      <div className="flex justify-end gap-2 pt-2">
        {onCancel && (
          <Button type="button" variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
        )}
        <Button type="submit" loading={loading} disabled={!title.trim()}>
          {mode === 'create' ? 'Create Task' : 'Save Changes'}
        </Button>
      </div>
    </form>
  );
}
