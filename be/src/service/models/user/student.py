from src.service.models.user.base_user import BaseUser


class Student(BaseUser):
    role: str = "student"
