from typing import List

from src.service.models.classroom.classroom_item import ClassroomItem


class CheckInForm(ClassroomItem):
    duration: str
    attendance_ids: List[str]
    absent_ids: List[str]
