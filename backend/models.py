from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class TaskBase(SQLModel):
    title: str
    completed: bool = False
    due_at: Optional[datetime] = None  # ISO8601 on the wire

class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class TaskCreate(TaskBase):
    pass

class TaskRead(TaskBase):
    id: int

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    completed: Optional[bool] = None
    due_at: Optional[datetime] = None
