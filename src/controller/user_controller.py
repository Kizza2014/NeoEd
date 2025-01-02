from src.service.models.user import UserResponse, UserUpdate
from src.repository.mysql.user import UserRepository
from fastapi import APIRouter, Depends
from src.configs.connections.mysql import get_mysql_connection
from typing import List
from fastapi import HTTPException
# from src.configs.dependencies import verify_token, get_current_user
from src.configs.logging import get_logger
from mysql.connector import Error as MySQLError


USER_CONTROLLER = APIRouter()
logger = get_logger(__name__)


# BASIC API
@USER_CONTROLLER.get("/me", response_model=UserResponse)
async def get_current_user_info(
    # username: str,
    connection=Depends(get_mysql_connection)
) -> UserResponse:
    user_repo = UserRepository(connection)
    user = await user_repo.get_by_username('hoangkimgiap')  # temporary, will be replaced by username from token

    if user is None:
        # logger.error(f"Your account is not available")
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

        status = await user_repo.update_by_username(current_user['username'], user_data)

        if not status:
            raise HTTPException(status_code=500, detail="Unexpected error occurred. Update user failed")

        return {
            'message': 'User profile updated successfully',
            'updated_info': user_data.model_dump(exclude_unset=True),
        }
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")


@USER_CONTROLLER.get("/user/{username}/detail", response_model=UserResponse)
async def get_by_username(username: str, connection=Depends(get_mysql_connection)):
    try:
        repo = UserRepository(connection)
        user = await repo.get_by_username(username)
        if not user:
            logger.error(f"User {username} not found")
            raise HTTPException(status_code=404, detail="User not found")

        return UserResponse(**user)
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")


# TEST API

@USER_CONTROLLER.get("/user/all", response_model=List[UserResponse])
async def get_all(connection=Depends(get_mysql_connection)):
    try:
        repo = UserRepository(connection)
        query_result = await repo.get_all()
        return [UserResponse(**user) for user in query_result]
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")


@USER_CONTROLLER.put("/user/{username}/update")
async def update_by_username(username: str, update_info: UserUpdate, connection=Depends(get_mysql_connection)):
    try:
        repo = UserRepository(connection)
        new_info = update_info.model_dump(exclude_unset=True)
        if len(new_info.keys()) == 0:
            return {
                'message': f"No update info provided for user {username}",
                'username': username,
                'new_info': new_info,
            }

        if not await repo.update_by_username(username, update_info):
            raise HTTPException(status_code=400, detail=f"Unexpected error occurred. Update user {username} failed")

        return {
            'message': f"Updated user {username} successfully",
            'username': username,
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