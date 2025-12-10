"""Task CRUD API routes.

Implements endpoints per /specs/features/task-crud.md:
- POST   /api/{user_id}/tasks              - Create task
- GET    /api/{user_id}/tasks              - List tasks
- GET    /api/{user_id}/tasks/{task_id}    - Get task
- PUT    /api/{user_id}/tasks/{task_id}    - Update task
- DELETE /api/{user_id}/tasks/{task_id}    - Delete task
- PATCH  /api/{user_id}/tasks/{task_id}/complete - Toggle completion
"""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select

from db import get_session
from models import Task
from schemas import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from auth import AuthenticatedUser, get_verified_user

router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Task created successfully"},
        401: {"description": "Unauthorized - invalid or missing token"},
        403: {"description": "Forbidden - user ID mismatch"},
        422: {"description": "Validation error"},
    },
)
async def create_task(
    user_id: UUID,
    task_data: TaskCreate,
    current_user: AuthenticatedUser = Depends(get_verified_user),
    session: Session = Depends(get_session),
) -> Task:
    """Create a new task for the authenticated user.

    - Title is required (1-255 characters)
    - Description is optional (max 2000 characters)
    - Task defaults to completed=false
    - Server generates id, created_at, updated_at
    """
    task = Task(
        user_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
        completed=False,
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.get(
    "",
    response_model=TaskListResponse,
    responses={
        200: {"description": "List of tasks"},
        401: {"description": "Unauthorized - invalid or missing token"},
        403: {"description": "Forbidden - user ID mismatch"},
    },
)
async def list_tasks(
    user_id: UUID,
    current_user: AuthenticatedUser = Depends(get_verified_user),
    session: Session = Depends(get_session),
) -> TaskListResponse:
    """List all tasks for the authenticated user.

    - Returns only tasks belonging to the authenticated user
    - Sorted by created_at descending (newest first)
    - Returns empty array if no tasks exist
    """
    statement = (
        select(Task)
        .where(Task.user_id == current_user.id)
        .order_by(Task.created_at.desc())
    )
    tasks = session.exec(statement).all()

    return TaskListResponse(tasks=tasks, count=len(tasks))


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    responses={
        200: {"description": "Task details"},
        401: {"description": "Unauthorized - invalid or missing token"},
        403: {"description": "Forbidden - user ID mismatch"},
        404: {"description": "Task not found"},
    },
)
async def get_task(
    user_id: UUID,
    task_id: UUID,
    current_user: AuthenticatedUser = Depends(get_verified_user),
    session: Session = Depends(get_session),
) -> Task:
    """Get a specific task by ID.

    - Returns 404 if task doesn't exist or belongs to another user
    - No information leakage about other users' tasks
    """
    task = session.get(Task, task_id)

    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    responses={
        200: {"description": "Task updated successfully"},
        401: {"description": "Unauthorized - invalid or missing token"},
        403: {"description": "Forbidden - user ID mismatch"},
        404: {"description": "Task not found"},
        422: {"description": "Validation error"},
    },
)
async def update_task(
    user_id: UUID,
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: AuthenticatedUser = Depends(get_verified_user),
    session: Session = Depends(get_session),
) -> Task:
    """Update a task's title and/or description.

    - Partial updates allowed (only provided fields are updated)
    - Cannot update id, user_id, created_at, or completed via this endpoint
    - updated_at is automatically refreshed
    """
    task = session.get(Task, task_id)

    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Apply partial updates
    update_data = task_data.model_dump(exclude_unset=True)

    if "title" in update_data:
        task.title = update_data["title"]

    if "description" in update_data:
        task.description = update_data["description"]

    # Refresh updated_at timestamp
    task.updated_at = datetime.now(timezone.utc)

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Task deleted successfully"},
        401: {"description": "Unauthorized - invalid or missing token"},
        403: {"description": "Forbidden - user ID mismatch"},
        404: {"description": "Task not found"},
    },
)
async def delete_task(
    user_id: UUID,
    task_id: UUID,
    current_user: AuthenticatedUser = Depends(get_verified_user),
    session: Session = Depends(get_session),
) -> Response:
    """Permanently delete a task.

    - Deletion is permanent (no soft delete)
    - Returns 404 if task doesn't exist or belongs to another user
    """
    task = session.get(Task, task_id)

    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    session.delete(task)
    session.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/{task_id}/complete",
    response_model=TaskResponse,
    responses={
        200: {"description": "Task completion toggled"},
        401: {"description": "Unauthorized - invalid or missing token"},
        403: {"description": "Forbidden - user ID mismatch"},
        404: {"description": "Task not found"},
    },
)
async def toggle_task_completion(
    user_id: UUID,
    task_id: UUID,
    current_user: AuthenticatedUser = Depends(get_verified_user),
    session: Session = Depends(get_session),
) -> Task:
    """Toggle task completion status.

    - Flips completed from false to true or true to false
    - updated_at is automatically refreshed
    """
    task = session.get(Task, task_id)

    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Toggle completion status
    task.completed = not task.completed
    task.updated_at = datetime.now(timezone.utc)

    session.add(task)
    session.commit()
    session.refresh(task)

    return task
