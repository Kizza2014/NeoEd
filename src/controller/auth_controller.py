from src.repository.mysql import UserRepository
from fastapi import APIRouter, Depends, Response, status, Cookie
from src.configs.connections.mysql import get_mysql_conn
from src.service.models.authentication import TokenResponse, UserLogin, RegisterResponse, UserCreate
from fastapi import HTTPException
from src.configs.security import verify_password, create_refresh_token, create_access_token, decode_refresh_token


AUTH_CONTROLLER = APIRouter()


@AUTH_CONTROLLER.post("/register", response_model=RegisterResponse)
async def register(user: UserCreate, conn=Depends(get_mysql_conn)):
    user_repo = UserRepository(conn)

    # Kiểm tra id tồn tại hay chưa
    existing_user = user_repo.get_by_id(user.id)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Tạo user mới
    finish_status = user_repo.insert(user)
    if not finish_status:
        raise HTTPException(status_code=400, detail="Unexpected error.")

    return RegisterResponse(
        message="User registered successfully",
        user_id=user.id,
    )


@AUTH_CONTROLLER.post("/login", response_model=TokenResponse)
async def signin(
    user: UserLogin,
    response: Response,
    conn=Depends(get_mysql_conn),
):
    user_repo = UserRepository(conn)

    # Kiểm tra email và password
    user_db = user_repo.get_by_id(user.id)
    if not user_db or not verify_password(user.password, user_db.user_passwd):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Tạo tokens
    access_token = create_access_token(user_db.id)
    refresh_token = create_refresh_token(user_db.id)

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
        user_id=user_db.id,
        roles=["user", "admin"],
    )


@AUTH_CONTROLLER.post("/refresh-token", response_model=TokenResponse)
async def refresh_token_(
    response: Response,
    conn=Depends(get_mysql_conn),
    refresh_token: str = Cookie(None),
):
    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="No refresh token provided",
        )

    user_repo = UserRepository(conn)

    payload = decode_refresh_token(refresh_token)
    if not payload or not payload.get("user_id"):
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    user = await user_repo.get_by_id(payload["user_id"])
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    access_token = create_access_token(user.user_id)
    new_refresh_token = create_refresh_token(user.user_id, exp=payload.get("exp"))

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
        user_id=user.user_id,
        roles=["user", "admin"],
    )


@AUTH_CONTROLLER.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="refresh_token")
    return {
        "message": "Logout successful",
    }