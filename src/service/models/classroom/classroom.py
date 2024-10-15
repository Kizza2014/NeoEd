from typing import *
from pydantic import BaseModel
from datetime import datetime


class Classroom(BaseModel):
    classroom_id: str
    class_name: str
    schedules: Dict[str, str]
    textbooks: List[str]
    created_at: datetime
    updated_at: datetime
