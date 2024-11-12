from src.service.models.classroom.classroom_item import ClassroomItem
from datetime import datetime


class Assignment(ClassroomItem):
    id: str
    tilte: str
    class_id: str
    author: str
    descriptions: str
    created_at: datetime
    updated_at: datetime
    start_at: datetime
    end_at: datetime
