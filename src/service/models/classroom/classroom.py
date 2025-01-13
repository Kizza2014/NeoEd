from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class ClassroomBase(BaseModel):
    id: str
    class_name: str
    subject_name: str
    class_schedule: Optional[str] = None
    description: Optional[str] = None
    owner_id: str
    owner_username: str
    owner_fullname: str


class ClassroomCreate(ClassroomBase):
    pass


class ClassroomUpdate(BaseModel):
    class_name: Optional[str] = None
    subject_name: Optional[str] = None
    class_schedule: Optional[str] = None
    description: Optional[str] = None


class ClassroomResponse(ClassroomBase):
    created_at: datetime
    updated_at: datetime

