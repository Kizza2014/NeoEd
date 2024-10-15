from src.service.models.classroom.classroom_item import ClassroomItem
from datetime import datetime


class Exercise(ClassroomItem):
    exercise_id: str
    name: str
    content: str
    deadline: datetime
    grade: float = None
