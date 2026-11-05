from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

class TaskStatus(str, Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"

class TaskCreate(BaseModel):
    title: str = Field(..., description="Title of the task (required)")
    description: Optional[str] = Field(default=None, description="Optional description of the task")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Task title cannot be empty or whitespace only")
        return stripped

class TaskStatusUpdate(BaseModel):
    status: TaskStatus = Field(..., description="Status must be either 'Pending' or 'Completed'")

class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    status: str
    created_at: datetime

