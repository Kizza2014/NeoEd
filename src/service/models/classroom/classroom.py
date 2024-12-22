from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class ClassroomBase(BaseModel):
    id: str = None
    class_name: str
    subject_name: str
    class_schedule: str
    owner: str


class ClassroomCreate(ClassroomBase):
    password: Optional[str] = None

    class Config:
        allow_mutation = True


class ClassroomUpdate(BaseModel):
    class_name: Optional[str] = None
    subject_name: Optional[str] = None
    class_schedule: Optional[str] = None
    owner: Optional[str] = None


class ClassroomUpdateResponse(BaseModel):
    message: str
    class_id: str
    new_info: dict


class ClassroomDeleteResponse(BaseModel):
    message: str
    class_id: str


class CreateResponse(BaseModel):
    message: str
    class_id: str


class ClassroomResponse(ClassroomBase):
    created_at: datetime
    updated_at: datetime


class ClassroomMongoDB(BaseModel):
    id: int


class ParticipantResponse(BaseModel):
    username: str
    joined_at: datetime

class AddParticipantResponse(BaseModel):
    message: str
    username: str


class RemoveParticipantResponse(BaseModel):
    message: str
    username: str