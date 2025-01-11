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


AUTH_CONTROLLER = APIRouter(tags=['Authentication'])


@AUTH_CONTROLLER.post("/register", response_model=RegisterResponse)
async def register(new_user: UserCreate, connection=Depends(get_mysql_connection)):
    try:
        user_repo = UserRepository(connection)

        existing_user = await user_repo.get_by_username(new_user.username)
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already existed",
            )

        # Tạo user mới
        if not await user_repo.create_user(new_user):
            raise HTTPException(
                status_code=500,
                detail="Unexpected error occurred. Cannot create user",
            )

        return RegisterResponse(
            message="User registered successfully",
            username=new_user.username,
        )
    except MySQLError as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except PasswordValidationError:
        raise HTTPException(status_code=400,
                            detail="Password must be at least 8 characters long and include at least one number.")
    except UsernameValidationError:
        raise HTTPException(status_code=400,
                            detail="Username must not exceed 50 characters and can only include alphanumeric "
                                   "characters.")


@AUTH_CONTROLLER.post("/login", response_model=TokenResponse)
async def signin(
    user: UserLogin,
    response: Response,
    conn=Depends(get_mysql_connection),
):
    user_repo = UserRepository(conn)

    # Kiểm tra username và password
    user_db = await user_repo.get_by_username(user.username)
    if not user_db:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username",)
    user_id = user_db['id']
    user_pwd = user_db['hashed_password']
    if not verify_password(user.password, user_pwd):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    # Tạo tokens
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)

    redis = RedisRepository(user_id)
    redis.save_refresh_token(refresh_token)

    # Set refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user_id,
        roles=["user", "admin"],
    )


@AUTH_CONTROLLER.post("/refresh-token", response_model=TokenResponse)
async def refresh_token_(
    response: Response,
    conn=Depends(get_mysql_connection),
    refresh_token: str = Cookie(None),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided",
        )

    user_repo = UserRepository(conn)

    payload = decode_refresh_token(refresh_token)
    if not payload or not payload.get("data"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = await user_repo.get_by_id(payload["data"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    redis = RedisRepository(user['id'])
    redis_rt = redis.get_refresh_token()

    if refresh_token != redis_rt:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    access_token = create_access_token(user['id'])
    new_refresh_token = create_refresh_token(user['id'], exp=payload.get("exp"))

    redis.save_refresh_token(new_refresh_token)

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user_id=user['id'],
        roles=["user", "admin"],
    )


@AUTH_CONTROLLER.post("/logout")
async def logout(access_token: str):
    user_data = decode_access_token(access_token)
    user_id = user_data['data']
    redis = RedisRepository(user_id)
    redis.delete_access_token()
    redis.delete_refresh_token()
    return {
        "message": "Logout successful",
    }
