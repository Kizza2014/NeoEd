from src.service.models.user_model import UserResponse, UserUpdate, UserUpdateResponse, UserDeleteResponse
from src.repository.mysql import UserRepository
from fastapi import APIRouter, Depends
from src.configs.connections.mysql import get_mysql_connection
from typing import List
from fastapi import HTTPException
from src.configs.dependencies import verify_token, get_current_user
from src.configs.logging import get_logger
from mysql.connector import Error as MySQLError


USER_CONTROLLER = APIRouter()
logger = get_logger(__name__)


# BASIC API

@USER_CONTROLLER.get("/user/{username}/detail", response_model=UserResponse)
async def get_by_username(username: str, connection=Depends(get_mysql_connection)):
    """
    Retrieves a user by their username.

    Args:
        username (str): The username of the user to retrieve.
        connection: The database connection dependency.

    Returns:
        UserResponse: The user information.

    Raises:
        HTTPException: If the user is not found or a database error occurs.
    """
    try:
        repo = UserRepository(connection)
        user = await repo.get_by_username(username)
        if not user:
            logger.error(f"User {username} not found")
            raise HTTPException(status_code=404, detail="User not found")

        return UserResponse(**user)
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# @USER_CONTROLLER.get("/me", response_model=UserResponse, )
# async def get_current_user_info(
#     user_id: str = Depends(verify_token), conn=Depends(get_mysql_connection)
# ) -> UserResponse:
#     """
#     Get current user's profile.
#
#     Args:
#         user_id (str): The ID of the current user.
#         conn: The database connection dependency.
#
#     Returns:
#         UserResponse: The current user's profile information.
#
#     Raises:
#         HTTPException: If the user is not found.
#     """
#     user_repo = UserRepository(conn)
#     user = user_repo.get_info_by_id(user_id)
#
#     if not user:
#         logger.error(f"Your account is not available")
#         raise HTTPException(status_code=404, detail="User not found")
#
#     return user
#
#
# @USER_CONTROLLER.put("/me", response_model=UserResponse)
# async def update_user_info(
#     user_data: UserUpdate,
#     current_user: UserResponse = Depends(get_current_user),
#     conn=Depends(get_mysql_connection),
# ):
#     """Update current user's profile"""
#     user_repo = UserRepository(conn)
#
#     try:
#         # Update user fields
#         for field, value in user_data.model_dump(exclude_unset=True).items():
#             setattr(current_user, field, value)
#
#         is_success = user_repo.update_by_id(current_user.id, user_data)
#
#         if not is_success:
#             logger.error("Unexpected error when updating user information.")
#             raise HTTPException(status_code=400, detail="Update failed")
#
#         return UserResponse(
#             user_id=current_user.id,
#             user_name=user_data.username,
#             gender=user_data.gender,
#             birthdate=user_data.birthdate,
#             address=user_data.address,
#             email=user_data.email,
#         )
#
#     except Exception as e:
#         logger.error(f"Error updating user profile: {str(e)}")
#         raise HTTPException(status_code=500, detail="Error updating user profile")


# TEST API

@USER_CONTROLLER.get("/users/all", response_model=List[UserResponse])
async def get_all(connection=Depends(get_mysql_connection)):
    """
    Retrieves all users.

    Args:
        connection: The database connection dependency.

    Returns:
        List[UserResponse]: A list of all users.

    Raises:
        HTTPException: If a database error occurs.
    """
    try:
        repo = UserRepository(connection)
        query_result = await repo.get_all()
        return [UserResponse(**user) for user in query_result]
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@USER_CONTROLLER.put("/users/{username}/update", response_model=UserUpdateResponse)
async def update_by_username(username: str, update_info: UserUpdate, connection=Depends(get_mysql_connection)):
    """
    Updates a user's information by their username.

    Args:
        username (str): The username of the user to update.
        update_info (UserUpdate): The new user data.
        connection: The database connection dependency.

    Returns:
        UserUpdateResponse: The response message and updated user information.

    Raises:
        HTTPException: If the update fails or a database error occurs.
    """
    try:
        repo = UserRepository(connection)
        new_info = update_info.model_dump(exclude_unset=True)
        if len(new_info.keys()) == 0:
            return UserUpdateResponse(
                message=f"No update info provided for user {username}",
                username=username,
                new_info=new_info,
            )

        if not await repo.update_by_username(username, update_info):
            raise HTTPException(status_code=400, detail=f"Unexpected error occurred. Update user {username} failed")

        return UserUpdateResponse(
            message=f"Updated user {username} successfully",
            username=username,
            new_info=new_info,
        )
    except MySQLError as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@USER_CONTROLLER.delete("/users/{username}/delete", response_model=UserDeleteResponse)
async def delete_by_id(username: str, connection=Depends(get_mysql_connection)):
    """
    Deletes a user by their username.

    Args:
        username (str): The username of the user to delete.
        connection: The database connection dependency.

    Returns:
        UserDeleteResponse: The response message indicating the result of the delete operation.

    Raises:
        HTTPException: If the delete operation fails or a database error occurs.
    """
    try:
        repo = UserRepository(connection)
        if not await repo.delete_by_username(username):
            raise HTTPException(status_code=400, detail=f"Unexpected error occurred. Delete user {username} failed")

        return UserDeleteResponse(message=f"Deleted user {username} successfully", username=username)
    except MySQLError as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")