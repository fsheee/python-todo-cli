'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Task, ApiError, TaskCreateInput, TaskUpdateInput } from '@/types';
import { api } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { useToast } from '@/lib/toast-context';
import { TaskList } from '@/components/tasks/TaskList';
import { QuickAddTask } from '@/components/tasks/QuickAddTask';
import { DeleteConfirmation } from '@/components/tasks/DeleteConfirmation';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { TaskForm } from '@/components/tasks/TaskForm';

export default function DashboardPage() {
  const router = useRouter();
  const { user } = useAuth();
  const { showToast } = useToast();

  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [deleteTask, setDeleteTask] = useState<Task | null>(null);
  const [deleting, setDeleting] = useState(false);

  const fetchTasks = useCallback(async () => {
    if (!user) return;
    try {
      const data = await api.getTasks(user.id);
      setTasks(data);
    } catch (err) {
      const error = err as ApiError;
      showToast('error', error.detail || 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  }, [user, showToast]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const handleAddTask = async (title: string) => {
    if (!user) return;
    try {
      const newTask = await api.createTask(user.id, { title });
      setTasks((prev) => [newTask, ...prev]);
      showToast('success', 'Task created');
    } catch (err) {
      const error = err as ApiError;
      showToast('error', error.detail || 'Failed to create task');
    }
  };

  const handleToggle = async (id: string) => {
    if (!user) return;
    try {
      const updated = await api.toggleComplete(user.id, id);
      setTasks((prev) => prev.map((t) => (t.id === id ? updated : t)));
    } catch (err) {
      const error = err as ApiError;
      showToast('error', error.detail || 'Failed to update task');
    }
  };

  const handleEdit = (id: string) => {
    router.push(`/tasks/${id}`);
  };

  const handleDeleteClick = (id: string) => {
    const task = tasks.find((t) => t.id === id);
    if (task) setDeleteTask(task);
  };

  const handleDeleteConfirm = async () => {
    if (!user || !deleteTask) return;
    setDeleting(true);
    try {
      await api.deleteTask(user.id, deleteTask.id);
      setTasks((prev) => prev.filter((t) => t.id !== deleteTask.id));
      showToast('success', 'Task deleted');
      setDeleteTask(null);
    } catch (err) {
      const error = err as ApiError;
      showToast('error', error.detail || 'Failed to delete task');
    } finally {
      setDeleting(false);
    }
  };

  const handleCreateTask = async (data: TaskCreateInput | TaskUpdateInput) => {
    if (!('title' in data) || !data.title) return;
    if (!user) return;
    try {
      const createData: TaskCreateInput = { title: data.title, description: data.description };
      const newTask = await api.createTask(user.id, createData);
      setTasks((prev) => [newTask, ...prev]);
      showToast('success', 'Task created');
      setShowTaskModal(false);
    } catch (err) {
      const error = err as ApiError;
      showToast('error', error.detail || 'Failed to create task');
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">My Tasks</h1>
        <Button onClick={() => setShowTaskModal(true)}>+ New Task</Button>
      </div>

      <div className="space-y-4">
        <QuickAddTask onAdd={handleAddTask} placeholder="Add a task..." />

        <TaskList
          tasks={tasks}
          loading={loading}
          onToggle={handleToggle}
          onEdit={handleEdit}
          onDelete={handleDeleteClick}
        />
      </div>

      {/* Create Task Modal */}
      {showTaskModal && (
        <Modal
          open={showTaskModal}
          onClose={() => setShowTaskModal(false)}
          title="Create New Task"
        >
          <TaskForm
            mode="create"
            onSubmit={handleCreateTask}
            onCancel={() => setShowTaskModal(false)}
          />
        </Modal>
      )}

      {/* Delete Confirmation */}
      {deleteTask && (
        <DeleteConfirmation
          taskTitle={deleteTask.title}
          onConfirm={handleDeleteConfirm}
          onCancel={() => setDeleteTask(null)}
          loading={deleting}
        />
      )}
    </div>
  );
}
