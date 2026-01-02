'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { Task, ApiError } from '@/types';
import { api } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { useToast } from '@/lib/toast-context';
import { Button } from '@/components/ui/Button';
import { TaskForm } from '@/components/tasks/TaskForm';
import { DeleteConfirmation } from '@/components/tasks/DeleteConfirmation';
import { Skeleton } from '@/components/ui/Skeleton';
import { formatDateTime } from '@/lib/utils';

export default function TaskDetailPage() {
  const router = useRouter();
  const params = useParams();
  const taskId = params.id as string;
  const { user } = useAuth();
  const { showToast } = useToast();

  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showDelete, setShowDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const fetchTask = useCallback(async () => {
    if (!user) return;
    try {
      const data = await api.getTask(user.id, taskId);
      setTask(data);
    } catch (err) {
      const error = err as ApiError;
      if (error.detail?.includes('404') || error.detail?.includes('not found')) {
        router.push('/dashboard');
      }
      showToast('error', error.detail || 'Failed to load task');
    } finally {
      setLoading(false);
    }
  }, [user, taskId, router, showToast]);

  useEffect(() => {
    fetchTask();
  }, [fetchTask]);

  const handleUpdate = async (data: { title?: string; description?: string }) => {
    if (!user || !task) return;
    setSaving(true);
    try {
      const updated = await api.updateTask(user.id, task.id, data);
      setTask(updated);
      setEditing(false);
      showToast('success', 'Task updated');
    } catch (err) {
      const error = err as ApiError;
      showToast('error', error.detail || 'Failed to update task');
    } finally {
      setSaving(false);
    }
  };

  const handleToggle = async () => {
    if (!user || !task) return;
    try {
      const updated = await api.toggleComplete(user.id, task.id);
      setTask(updated);
    } catch (err) {
      const error = err as ApiError;
      showToast('error', error.detail || 'Failed to update task');
    }
  };

  const handleDelete = async () => {
    if (!user || !task) return;
    setDeleting(true);
    try {
      await api.deleteTask(user.id, task.id);
      showToast('success', 'Task deleted');
      router.push('/dashboard');
    } catch (err) {
      const error = err as ApiError;
      showToast('error', error.detail || 'Failed to delete task');
    } finally {
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton variant="text" width="30%" height={24} />
        <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
          <Skeleton variant="text" width="60%" height={28} />
          <Skeleton variant="text" width="40%" height={16} />
          <Skeleton variant="rectangular" width="100%" height={100} />
        </div>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Task not found</h2>
        <p className="text-gray-600 mb-4">This task doesn&apos;t exist or you don&apos;t have access.</p>
        <Link href="/dashboard" className="text-primary-600 hover:text-primary-700">
          ← Back to dashboard
        </Link>
      </div>
    );
  }

  return (
    <div>
      <Link
        href="/dashboard"
        className="inline-flex items-center gap-1 text-gray-600 hover:text-gray-900 mb-4"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Back to tasks
      </Link>

      <div className="bg-white rounded-lg border border-gray-200">
        {editing ? (
          <div className="p-6">
            <TaskForm
              mode="edit"
              initialData={{ title: task.title, description: task.description || '' }}
              onSubmit={handleUpdate}
              onCancel={() => setEditing(false)}
              loading={saving}
            />
          </div>
        ) : (
          <>
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <h1 className="text-xl font-semibold text-gray-900">{task.title}</h1>
                <Button variant="secondary" size="sm" onClick={() => setEditing(true)}>
                  Edit
                </Button>
              </div>

              <div className="flex items-center gap-2 mb-4">
                <button
                  onClick={handleToggle}
                  className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm ${
                    task.completed
                      ? 'bg-green-100 text-green-700'
                      : 'bg-gray-100 text-gray-700'
                  }`}
                >
                  {task.completed ? (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      Complete
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <circle cx="12" cy="12" r="10" strokeWidth={2} />
                      </svg>
                      Incomplete
                    </>
                  )}
                </button>
              </div>

              {task.description && (
                <div className="mb-4">
                  <h2 className="text-sm font-medium text-gray-700 mb-1">Description</h2>
                  <p className="text-gray-600 whitespace-pre-wrap">{task.description}</p>
                </div>
              )}

              <div className="text-sm text-gray-500 space-y-1">
                <p>Created: {formatDateTime(task.created_at)}</p>
                <p>Updated: {formatDateTime(task.updated_at)}</p>
              </div>
            </div>

            <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
              <Button variant="danger" size="sm" onClick={() => setShowDelete(true)}>
                Delete Task
              </Button>
            </div>
          </>
        )}
      </div>

      {showDelete && (
        <DeleteConfirmation
          taskTitle={task.title}
          onConfirm={handleDelete}
          onCancel={() => setShowDelete(false)}
          loading={deleting}
        />
      )}
    </div>
  );
}
