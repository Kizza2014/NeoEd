from src.repository.mysql.notification import NotificationRepository
from src.repository.mysql.user import UserRepository
from fastapi import APIRouter, Depends, Response, status, Cookie
from src.configs.connections.mysql import get_mysql_connection
from src.repository.redis.redis_repository import RedisRepository
from src.service.models.authentication import TokenResponse, UserLogin
from src.service.models.user.user_model import RegisterResponse, UserCreate
from src.service.models.exceptions.register_exception import PasswordValidationError, UsernameValidationError
from fastapi import HTTPException
from src.service.authentication.utils import *
from mysql.connector import Error as MySQLError

from src.service.notification.notification_service import NotificationService

NOTIFICATION_CONTROLLER = APIRouter(tags=['Notification'])


@NOTIFICATION_CONTROLLER.post("/notifications/create")
def create_notification_(title: str,
                         content: str,
                         class_id: str,
                         cnx=Depends(get_mysql_connection)):
    notification_service = NotificationService(class_id, cnx)
    notification_service.create_new_notification_for_students(title, content, "none")


@NOTIFICATION_CONTROLLER.get("/notifications/{notification_id}")
def get_notification_(notification_id: str,
                      cnx=Depends(get_mysql_connection)):
    notification_repo = NotificationRepository(cnx)
    return notification_repo.get_by_id(notification_id)


@NOTIFICATION_CONTROLLER.get("/notifications/user/{user_id}")
def get_notification_of_user_(user_id: str,
                              cnx=Depends(get_mysql_connection)):
    notification_repo = NotificationRepository(cnx)
    return notification_repo.get_notifications_of_user(user_id)


@NOTIFICATION_CONTROLLER.patch("/notifications/set-read")
def set_read_(user_id: str, notification_id: str, read_status: bool,
              cnx=Depends(get_mysql_connection)):
    notification_repo = NotificationRepository(cnx)
    try:
        notification_repo.set_read_status(user_id, notification_id, read_status)
        return True
    except Exception as e:
        return False
