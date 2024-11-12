from typing import *
from pydantic import BaseModel
from datetime import datetime


class Classroom(BaseModel):
    id: str
    class_name: str
    semester: str
    room_id: str
    subject_name: str
    class_schedule: str
    created_at: datetime
    updated_at: datetime