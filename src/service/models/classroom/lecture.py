from pydantic import BaseModel
from src.service.models.classroom.classroom_item import ClassroomItem


class Lecture(ClassroomItem):
    lecture_id: str
    name: str
    content: str
