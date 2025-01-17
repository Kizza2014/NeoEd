from src.service.models.user import UserResponse, UserUpdate
from src.repository.mysql.user import UserRepository
from fastapi import APIRouter, Depends
from src.configs.connections.mysql import get_mysql_connection
from fastapi import HTTPException, Depends, Form
from src.configs.logging import get_logger
from mysql.connector import Error as MySQLError
from src.service.authentication.utils import *
from src.controller.utils import get_mysql_repo
from src.service.models.exceptions.register_exception import EmailValidationError
from typing import List
from datetime import date


USER_CONTROLLER = APIRouter(tags=['User'])
logger = get_logger(__name__)


# BASIC API
@USER_CONTROLLER.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user_id: str=Depends(verify_token),
    mysql_cnx=Depends(get_mysql_connection)
) -> UserResponse:
    if not user_id:
        raise HTTPException(status_code=403, detail='Unauthorized. Try to login again before accessing this resource.')

    mysql_repo = await get_mysql_repo(mysql_cnx)
    user = await mysql_repo['user'].get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**user)


@USER_CONTROLLER.put("/me/update")
async def update_user_info(
    fullname: str=Form(None),
    gender: str=Form(None),
    birthdate: date=Form(None),
    email: str=Form(None),
    address: str=Form(None),
    user_id: str=Depends(verify_token),
    mysql_cnx=Depends(get_mysql_connection),
):
    try:
        if not user_id:
            raise HTTPException(status_code=403, detail='Unauthorized. Try to login again before accessing this resource.')

        info = {
            'fullname': fullname if fullname else None,
            'gender': gender if gender else None,
            'birthdate': birthdate if birthdate else None,
            'email': email if email else None,
            'address': address if address else None,
        }
        info = {k:v for k,v in info.items() if v is not None}
        user_data = UserUpdate(**info)
        mysql_repo = await get_mysql_repo(mysql_cnx)
        if not await mysql_repo['user'].update_by_id(user_id, user_data):
            raise HTTPException(status_code=500, detail="Unexpected error occurred. Update user failed")

        return {
            'message': 'User profile updated successfully',
            'updated_info': user_data.model_dump(exclude_unset=True),
        }
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")
    except EmailValidationError as e:
        raise HTTPException(status_code=400, detail='Invalid email format')


@USER_CONTROLLER.get("/user/{user_id}/detail", response_model=UserResponse)
async def get_by_id(user_id: str, connection=Depends(get_mysql_connection)):
    try:
        repo = UserRepository(connection)
        user = await repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse(**user)
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")


@USER_CONTROLLER.get("/user/all", response_model=List[UserResponse])
async def get_all(connection=Depends(get_mysql_connection)):
    try:
        repo = UserRepository(connection)
        query_result = await repo.get_all()
        return [UserResponse(**user) for user in query_result]
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")


@USER_CONTROLLER.put("/user/{user_id}/update")
async def update_by_id(user_id: str, update_info: UserUpdate, connection=Depends(get_mysql_connection)):
    try:
        repo = UserRepository(connection)
        new_info = update_info.model_dump(exclude_unset=True)
        if len(new_info.keys()) == 0:
            return {
                'message': f"No update info provided for user {user_id}",
                'username': user_id,
                'new_info': new_info,
            }

        if not await repo.update_by_id(user_id, update_info):
            raise HTTPException(status_code=400, detail=f"Unexpected error occurred. Update user {user_id} failed")

        return {
            'message': f"Updated user {user_id} successfully",
            'username': user_id,
            'new_info': new_info,
        }
    except MySQLError as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")


@USER_CONTROLLER.delete("/user/{username}/delete")
async def delete_by_id(username: str, connection=Depends(get_mysql_connection)):
    try:
        repo = UserRepository(connection)
        if not await repo.delete_by_username(username):
            raise HTTPException(status_code=400, detail=f"Unexpected error occurred. Delete user {username} failed")

        return {
            'message': f"Deleted user {username} successfully",
            'username': username
        }
    except MySQLError as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")