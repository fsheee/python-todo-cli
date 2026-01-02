'use client';

import { TaskListProps } from '@/types';
import { TaskItem } from './TaskItem';
import { TaskListSkeleton } from '../ui/Skeleton';
import { NoTasksEmptyState } from '../layout/EmptyState';

export function TaskList({
  tasks,
  loading = false,
  onToggle,
  onEdit,
  onDelete,
}: TaskListProps) {
  if (loading) {
    return <TaskListSkeleton count={5} />;
  }

  if (tasks.length === 0) {
    return <NoTasksEmptyState onAddTask={() => {}} />;
  }

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onToggle={onToggle}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
