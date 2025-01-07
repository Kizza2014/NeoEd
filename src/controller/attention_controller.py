import json
import uuid

from fastapi import BackgroundTasks, Query

from src.repository.mysql.user import UserRepository
from fastapi import APIRouter, Depends, Response, status, Cookie
from src.configs.connections.mysql import get_mysql_connection, get_mysql_cnx
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


@ATTN_CONTROLLER.get("/checkin/sessions-of-class")
def get_sessions_from_class_(class_id: str = Query(...)):
    cnx = get_mysql_cnx()
    query = """
    SELECT `check_in_session`.`session_id`,
    `check_in_session`.`class_id`,
    `check_in_session`.`creator`,
    `check_in_session`.`data`,
    `check_in_session`.`started_at`,
    `check_in_session`.`done`,
    `check_in_session`.`ended_at`
    FROM `check_in_session`
    WHERE `check_in_session`.`class_id` = %s
    """
    try:
        cur = cnx.cursor()
        cur.execute(query, (class_id,))
        rows = cur.fetchall()
        return [
            {
                'session_id': row[0],
                'class_id': row[1],
                'creator': row[2],
                'data': json.loads(row[3]),
                'started_at': row[4],
                'ended_at': row[6],
                'done': row[5]
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    finally:
        cnx.close()


@ATTN_CONTROLLER.get("/checkin/{session_id}")
def get_details_from_session_(session_id: str):
    cnx = get_mysql_cnx()
    query = """
    SELECT `check_in_session`.`session_id`,
    `check_in_session`.`class_id`,
    `check_in_session`.`creator`,
    `check_in_session`.`data`,
    `check_in_session`.`started_at`,
    `check_in_session`.`done`,
    `check_in_session`.`ended_at`
    FROM `check_in_session`
    WHERE session_id = %s
    """
    try:
        cur = cnx.cursor()
        cur.execute(query, (session_id,))
        row = cur.fetchone()
        print(row)
        return {
            'session_id': row[0],
            'class_id': row[1],
            'creator': row[2],
            'data': json.loads(row[3]),
            'started_at': row[4],
            'ended_at': row[6],
            'done': row[5]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    finally:
        cnx.close()


@ATTN_CONTROLLER.post("/absents/new-request")
def create_absents_request(class_id: str,
                           student_id: str,
                           absent_on: date,
                           reason: str):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED
    )


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
