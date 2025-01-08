from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from src.repository.mysql import UserRepository
from src.configs.connections.mysql import get_mysql_connection
from src.configs.logging import get_logger
from src.configs.security import decode_access_token, http_bearer
from src.configs.settings import get_settings
from src.service.models.user import UserResponse

logger = get_logger(__name__)

settings = get_settings()

async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    conn = Depends(get_mysql_connection),
) -> UserResponse:
    payload = decode_access_token(token.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("user_id", None)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repo = UserRepository(conn)
    user = user_repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


# Những Endpoints cần phải đăng nhập mới dùng được
async def verify_token(token: HTTPAuthorizationCredentials = Depends(http_bearer)):
    payload = decode_access_token(token.credentials)
    return payload["user_id"]
