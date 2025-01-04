from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class ClassroomBase(BaseModel):
    id: str
    class_name: str
    subject_name: str
    class_schedule: str
    description: Optional[str] = None
    owner_id: str
    require_password: bool = False


class ClassroomCreate(ClassroomBase):
    password: Optional[str] = None


class ClassroomUpdate(BaseModel):
    class_name: Optional[str] = None
    subject_name: Optional[str] = None
    class_schedule: Optional[str] = None
    description: Optional[str] = None
    password: Optional[str] = None
    require_password: Optional[bool] = None


class ClassroomResponse(ClassroomBase):
    created_at: datetime
    updated_at: datetime


class ParticipantResponse(BaseModel):
    username: str
    joined_at: datetime
