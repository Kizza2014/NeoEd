from src.service.models.notification.base_notification import BaseNotification


class DeadlineNotification(BaseNotification):
    title = "Sắp đến hạn"
    exercise_id: str
    time_remain: str