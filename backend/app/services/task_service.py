from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Task
from app.schemas import TaskCreate, TaskStatusUpdate

class TaskService:
    @staticmethod
    def get_all_tasks(db: Session) -> List[Task]:
        """Retrieve all tasks from the database ordered by newest first."""
        return db.query(Task).order_by(Task.id.desc()).all()

    @staticmethod
    def get_task_by_id(db: Session, task_id: int) -> Optional[Task]:
        """Find a task by its primary key ID."""
        return db.query(Task).filter(Task.id == task_id).first()

    @staticmethod
    def create_task(db: Session, task_in: TaskCreate) -> Task:
        """Create a new task with default Pending status."""
        new_task = Task(
            title=task_in.title,
            description=task_in.description,
            status="Pending"
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task

    @staticmethod
    def update_task_status(db: Session, task_id: int, status_in: TaskStatusUpdate) -> Optional[Task]:
        """Update the status of an existing task."""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        task.status = status_in.status.value
        db.commit()
        db.refresh(task)
        return task

