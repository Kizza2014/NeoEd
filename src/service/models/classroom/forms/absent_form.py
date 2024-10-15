from src.service.models.classroom.classroom_item import ClassroomItem


class AbsentForm(ClassroomItem):
    student_name: str
    student_code: str
    absent_at: str
    reason: str
