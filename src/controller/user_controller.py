from src.service.models.user import UserResponse, UserUpdate
from src.repository.mysql.user import UserRepository
from fastapi import APIRouter, Depends
from src.configs.connections.mysql import get_mysql_connection
from fastapi import HTTPException, Depends
from src.configs.logging import get_logger
from mysql.connector import Error as MySQLError
from src.service.authentication.utils import *
from typing import List


USER_CONTROLLER = APIRouter(tags=['User'])
logger = get_logger(__name__)


# BASIC API
@USER_CONTROLLER.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user_id: str=Depends(verify_token),
    connection=Depends(get_mysql_connection)
) -> UserResponse:
    if not user_id:
        raise HTTPException(status_code=403, detail='Unauthorized. Try to login again before accessing this resource.')

    user_repo = UserRepository(connection)
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**user)


@USER_CONTROLLER.put("/me/update")
async def update_user_info(
    # current_user: UserResponse,
    user_data: UserUpdate,
    connection=Depends(get_mysql_connection),
):
    try:
        user_repo = UserRepository(connection)
        current_user = await user_repo.get_by_username('hoangkimgiap') # temporary, will be replaced by username from token

        status = await user_repo.update_by_id(current_user['id'], user_data)

        if not status:
            raise HTTPException(status_code=500, detail="Unexpected error occurred. Update user failed")

        return {
            'message': 'User profile updated successfully',
            'updated_info': user_data.model_dump(exclude_unset=True),
        }
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")


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