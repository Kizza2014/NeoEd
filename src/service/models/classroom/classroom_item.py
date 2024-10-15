from abc import ABC
from pydantic import BaseModel
from datetime import datetime


class ClassroomItem(ABC, BaseModel):
    classroom_id: str
    created_at: datetime
    updated_at: datetime
    creator_id: str
