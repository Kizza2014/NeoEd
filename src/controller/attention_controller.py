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
from datetime import date

ATTN_CONTROLLER = APIRouter(tags=['Attention'])


@ATTN_CONTROLLER.get("/absents/{class_id}")
def get_absents_from_class_(class_id: str,
                            class_date: date):
    return True


@ATTN_CONTROLLER.post("/absents/new-request")
def create_absents_request(class_id: str,
                           student_id: str,
                           absent_on: date,
                           reason: str):
    pass


@ATTN_CONTROLLER.post("/checkin/new")
def create_new_checkin_session_(class_id: str,
                                duration: int):
    pass


