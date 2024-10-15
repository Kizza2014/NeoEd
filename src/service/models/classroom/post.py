from src.service.models.classroom.classroom_item import ClassroomItem


class Post(ClassroomItem):
    post_id: str
    name: str
    content: str
