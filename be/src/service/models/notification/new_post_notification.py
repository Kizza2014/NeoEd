from src.service.models.notification.base_notification import BaseNotification


class NewPostNotification(BaseNotification):
    title = "Bài đăng mới"
    post_id: str
