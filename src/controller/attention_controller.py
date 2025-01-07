import uuid

from fastapi import BackgroundTasks

from src.repository.mysql.user import UserRepository
from fastapi import APIRouter, Depends, Response, status, Cookie
from src.configs.connections.mysql import get_mysql_connection
from src.repository.redis.check_in_repository import CheckInRepository
from src.repository.redis.redis_repository import RedisRepository
from src.service.checkin.check_in_service import CheckInService
from src.service.models.authentication import TokenResponse, UserLogin
from src.service.models.user.user_model import RegisterResponse, UserCreate
from src.service.models.exceptions.register_exception import PasswordValidationError, UsernameValidationError
from fastapi import HTTPException
from src.service.authentication.utils import *
from mysql.connector import Error as MySQLError
from datetime import date

ATTN_CONTROLLER = APIRouter(tags=['Attention'])


def background_attention_task(class_id, session_id, creator_id, duration):
    check_in_service = CheckInService(class_id, session_id, creator_id, duration)
    if check_in_service.synchronize_mysql():
        check_in_service.destroy()
    else:
        raise RuntimeError("Can not synchronize with MySQL. Saving on Redis only.")


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
                                creator_id: str):
    session_id = 'ss-' + str(uuid.uuid4())
    check_in_service = CheckInService(class_id, session_id, creator_id)
    check_in_service.initialize()
    if session_id:
        return {"session_id": session_id}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create new check-in session. Please try again later."
        )


@ATTN_CONTROLLER.post("/checkin/end-session")
def end_session_(session_id: str, class_id: str):
    check_in_service = CheckInService(session_id=session_id, class_id=class_id)
    check_in_service.synchronize_mysql()
    check_in_service.destroy()
    return {"msg": "Session ended successfully!"}


@ATTN_CONTROLLER.get("/checkin/current")
def get_current_ci_session(class_id: str):
    session_id = CheckInRepository.get_current_session(class_id)
    return session_id


@ATTN_CONTROLLER.post("/checkin/student")
def student_checkin_(student_id: str,
                     session_id: str):
    try:
        CheckInRepository(session_id=session_id).check_in(student_id)
        return {"msg": "Successfully checked-in!"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
