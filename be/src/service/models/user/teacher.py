from src.service.models.user.base_user import BaseUser


class Teacher(BaseUser):
    role: str = "teacher"
