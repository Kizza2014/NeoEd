from src.service.models.classroom.classroom_item import ClassroomItem


class Post(ClassroomItem):
    id: str
    title: str
    class_id: str
    author: str
    created_at: str
    updated_at: str
    content: str
