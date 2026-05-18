"""
Task REST endpoints for CRUD operations.

Provides direct REST API for tasks (alternative to chat commands).

Spec Reference: specs/api/rest-tasks.md
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query

from app.schemas.tasks import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from app.middleware.auth import verify_jwt_token, security
from app.database import get_db_session
from app.models import Task

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _task_to_response(task: Task) -> TaskResponse:
    """Convert database Task model to TaskResponse schema."""
    return TaskResponse(
        id=str(task.id),
        title=task.title,
        description=task.description,
        status=task.status or "pending",
        priority=task.priority or "medium",
        due_date=task.due_date.isoformat() if task.due_date else None,
        user_id=str(task.user_id),
        created_at=task.created_at.isoformat() if task.created_at else datetime.utcnow().isoformat(),
        updated_at=task.updated_at.isoformat() if task.updated_at else datetime.utcnow().isoformat(),
    )


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: pending, in_progress, completed"),
    priority: Optional[str] = Query(None, description="Filter by priority: low, medium, high"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, alias="page_size", description="Items per page"),
    credentials = Depends(security),
):
    """
    List all tasks for the authenticated user.

    Supports filtering by status and priority.
    Pagination supported via page and page_size.
    """
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException:
        raise

    async with get_db_session() as session:
        # Build query
        from sqlalchemy import select, func, and_

        conditions = [Task.user_id == user_id]
        if status_filter:
            conditions.append(Task.status == status_filter)
        if priority:
            conditions.append(Task.priority == priority)

        # Get total count
        count_query = select(func.count(Task.id)).where(and_(*conditions))
        total = await session.scalar(count_query) or 0

        # Get paginated tasks
        offset = (page - 1) * page_size
        query = (
            select(Task)
            .where(and_(*conditions))
            .order_by(Task.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await session.execute(query)
        tasks = result.scalars().all()

        return TaskListResponse(
            tasks=[_task_to_response(t) for t in tasks],
            total=total,
            page=page,
            page_size=page_size,
        )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    credentials = Depends(security),
):
    """Get a specific task by ID."""
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException:
        raise

    async with get_db_session() as session:
        from sqlalchemy import select
        query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )

        return _task_to_response(task)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    credentials = Depends(security),
):
    """Create a new task."""
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException:
        raise

    import uuid as uuid_lib

    async with get_db_session() as session:
        from sqlalchemy import select
        from app.models import User

        # Verify user exists (cast string user_id to UUID for comparison)
        user_result = await session.execute(select(User).where(User.id == uuid_lib.UUID(user_id)))
        user = user_result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Create task
        task = Task(
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            user_id=user_id,
            status="pending",
        )

        if task_data.due_date:
            from datetime import datetime
            task.due_date = datetime.fromisoformat(task_data.due_date.replace("Z", "+00:00"))

        session.add(task)
        await session.commit()
        await session.refresh(task)

        return _task_to_response(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    credentials = Depends(security),
):
    """Update an existing task."""
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException:
        raise

    async with get_db_session() as session:
        from sqlalchemy import select
        query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )

        # Update fields
        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description
        if task_data.status is not None:
            task.status = task_data.status
        if task_data.priority is not None:
            task.priority = task_data.priority
        if task_data.due_date is not None:
            from datetime import datetime
            task.due_date = datetime.fromisoformat(task_data.due_date.replace("Z", "+00:00"))

        task.updated_at = datetime.now(timezone.utc)

        await session.commit()
        await session.refresh(task)

        return _task_to_response(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    credentials = Depends(security),
):
    """Delete a task."""
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException:
        raise

    async with get_db_session() as session:
        from sqlalchemy import select, delete
        query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )

        await session.delete(task)
        await session.commit()