from src.service.models.user import UserInfo, UserUpdate
from src.repository.mysql import UserRepository
from fastapi import APIRouter, Depends
from src.configs.connections.mysql import get_mysql_conn
# from typing import List
# from src.service.models import BaseUser
from fastapi import HTTPException
from src.configs.dependencies import verify_token, get_current_user
from src.configs.logging import get_logger
# from fastapi.openapi.models import SecurityScheme


USER_CONTROLLER = APIRouter()
logger = get_logger(__name__)


# BASIC API

@USER_CONTROLLER.get("/user/{user_id}", response_model=UserInfo)
async def get_by_id(user_id: str, conn=Depends(get_mysql_conn)):
    repo = UserRepository(conn)
    return repo.get_by_id(user_id)

@USER_CONTROLLER.get("/me", response_model=UserInfo,)
async def get_current_user_info(
    user_id: str = Depends(verify_token), conn=Depends(get_mysql_conn)
) -> UserInfo:
    """Get current user's profile"""
    user_repo = UserRepository(conn)
    user = user_repo.get_info_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@USER_CONTROLLER.put("/me", response_model=UserInfo)
async def update_user_info(
    user_data: UserUpdate,
    current_user: UserInfo = Depends(get_current_user),
    conn=Depends(get_mysql_conn),
):
    """Update current user's profile"""
    user_repo = UserRepository(conn)

    try:
        # Update user fields
        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(current_user, field, value)

        is_success = user_repo.update_by_id(current_user.id, user_data)

        if not is_success:
            logger.error("Unexpected error when updating user information.")
            raise HTTPException(status_code=400, detail="Update failed")

        return UserInfo(
            user_id=current_user.id,
            user_name=user_data.username,
            gender=user_data.gender,
            birthdate=user_data.birthdate,
            address=user_data.address,
            email=user_data.email,
        )

    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating user profile")


# ADMIN API

# @USER_CONTROLLER.get("/users", response_model=List[UserInfo])
# async def get_all(conn=Depends(get_mysql_conn)):
#     repo = UserRepository(conn)
#     return repo.get_all()
#
#
# @USER_CONTROLLER.put("/users/{user_id}")
# async def update_by_id(user_id: str, new_item: BaseUser, conn=Depends(get_mysql_conn)):
#     repo = UserRepository(conn)
#     if not repo.update_by_id(user_id, new_item):
#         return False
#     return new_item
#
#
# @USER_CONTROLLER.post("/users")
# async def create(new_user: BaseUser, conn=Depends(get_mysql_conn)):
#     repo = UserRepository(conn)
#     if not repo.insert(new_user):
#         return False
#     return new_user
#
#
# @USER_CONTROLLER.delete("/users/{user_id}")
# async def delete_by_id(user_id: str, conn=Depends(get_mysql_conn)):
#     repo = UserRepository(conn)
#     return repo.delete_by_id(user_id)