import uuid
from datetime import datetime

from fastapi import Depends
from mysql.connector.pooling import PooledMySQLConnection

from src.repository.mysql.notification import NotificationRepository
from src.configs.connections.mysql import get_mysql_connection, MySQLConnection
from src.service.models.notification.base_notification import BaseNotification


class NotificationService:
    def __init__(self, class_id: str, connection):
        self.class_id = class_id
        self.cnx = connection

    def create_new_notification_for_students(self, title: str, content: str, direct_url=str):
        try:
            notification_repo = NotificationRepository(self.cnx)
            new_notification = BaseNotification(
                title=title,
                content=content,
                direct_url=direct_url,
                class_id=self.class_id
            )
            notification_repo.insert(new_notification)
            notification_repo.queue_notifications_for_students(new_notification)
            self.cnx.commit()
        except Exception as e:
            self.cnx.rollback()
            raise e



