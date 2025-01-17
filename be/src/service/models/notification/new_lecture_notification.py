from src.service.models.notification.base_notification import BaseNotification


class NewLectureNotification(BaseNotification):
    title = "Bài giảng mới"
    lecture_id: str
