from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Assignment(BaseModel):
    id: str
    title: str
    author: str
    descriptions: str
    created_at: datetime
    updated_at: datetime
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None


class AssignmentCreate(BaseModel):
    title: str
    author: str
    descriptions: str
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None

class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    descriptions: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
