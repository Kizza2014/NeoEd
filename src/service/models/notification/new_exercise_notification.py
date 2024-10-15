from src.service.models.notification.base_notification import BaseNotification


class NewExerciseNotification(BaseNotification):
    title = "Bài tập mới"
    exercise_id: str
