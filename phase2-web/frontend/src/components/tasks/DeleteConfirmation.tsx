'use client';

import { DeleteConfirmationProps } from '@/types';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';

export function DeleteConfirmation({
  taskTitle,
  onConfirm,
  onCancel,
  loading = false,
}: DeleteConfirmationProps) {
  return (
    <Modal
      open={true}
      onClose={onCancel}
      title="Delete Task"
      actions={
        <>
          <Button variant="secondary" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
          <Button variant="danger" onClick={onConfirm} loading={loading}>
            Delete
          </Button>
        </>
      }
    >
      <p className="text-gray-600">
        Are you sure you want to delete &quot;{taskTitle}&quot;?
      </p>
      <p className="text-sm text-gray-500 mt-2">
        This action cannot be undone.
      </p>
    </Modal>
  );
}
