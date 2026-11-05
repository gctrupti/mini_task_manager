from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import TaskCreate, TaskResponse, TaskStatusUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get(
    "/",
    response_model=List[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve all tasks"
)
def get_all_tasks(db: Session = Depends(get_db)):
    """
    Retrieve all tasks in the system.
    Returns an empty JSON array if there are no tasks.
    """
    return TaskService.get_all_tasks(db)

@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task"
)
def create_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    """
    Create a new task:
    - Accepts title (required, non-empty) and description (optional).
    - Status is automatically assigned as 'Pending'.
    - Persisted into SQLite.
    - Returns HTTP 201 Created.
    """
    return TaskService.create_task(db=db, task_in=task_in)

@router.patch(
    "/{id}/",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update task status"
)
def update_task_status(
    id: int,
    status_in: TaskStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Update the status of an existing task:
    - Accepts 'Pending' or 'Completed'.
    - Returns HTTP 200 with the updated task.
    - Returns HTTP 404 if the task ID does not exist.
    """
    task = TaskService.update_task_status(db=db, task_id=id, status_in=status_in)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {id} not found"
        )
    return task

@router.delete(
    "/{id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task"
)
def delete_task(id: int, db: Session = Depends(get_db)):
    """
    Delete a task by primary key ID:
    - Returns HTTP 204 No Content on successful deletion.
    - Returns HTTP 404 if the task ID does not exist.
    """
    deleted = TaskService.delete_task(db=db, task_id=id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {id} not found"
        )
    return None

