from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import TaskModel
from app.schemas import Task, TaskCreate, TaskStatus, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


def to_task_schema(task: TaskModel) -> Task:
    return Task(
        id=UUID(task.id),
        title=task.title,
        description=task.description,
        status=TaskStatus(task.status),
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.get("", response_model=list[Task])
def list_tasks(
    db: Annotated[Session, Depends(get_db)],
    status_filter: Annotated[TaskStatus | None, Query(alias="status")] = None,
):
    statement = select(TaskModel)

    if status_filter is not None:
        statement = statement.where(TaskModel.status == status_filter.value)

    task_models = db.scalars(statement).all()
    return [to_task_schema(task) for task in task_models]


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: UUID, db: Annotated[Session, Depends(get_db)]):
    task = db.get(TaskModel, str(task_id))

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return to_task_schema(task)


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Annotated[Session, Depends(get_db)]):
    now = datetime.now(UTC)

    task = TaskModel(
        title=payload.title,
        description=payload.description,
        status=payload.status.value,
        created_at=now,
        updated_at=now,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return to_task_schema(task)


@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: UUID,
    payload: TaskUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    task = db.get(TaskModel, str(task_id))

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if payload.title is not None:
        task.title = payload.title

    if payload.description is not None:
        task.description = payload.description

    if payload.status is not None:
        task.status = payload.status.value

    task.updated_at = datetime.now(UTC)

    db.commit()
    db.refresh(task)

    return to_task_schema(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: UUID, db: Annotated[Session, Depends(get_db)]):
    task = db.get(TaskModel, str(task_id))

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    db.delete(task)
    db.commit()