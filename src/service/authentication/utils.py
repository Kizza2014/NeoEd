import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import datetime
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from passlib.context import CryptContext
from pytz import timezone

SECRET_KEY = "minhdeptrai"
ALGORITHM = 'HS256'
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
http_bearer = HTTPBearer()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data, expires_in=15) -> str:
    payload = {
        'data': data,
        'exp': datetime.datetime.now(timezone('Asia/Ho_Chi_Minh')) + datetime.timedelta(minutes=expires_in)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data, exp=None, expires_in=7) -> str:
    if exp:
        payload = {
            "data": data,
            "exp": exp
        }
    else:
        payload = {
            "data": data,
            "exp": datetime.datetime.now(timezone('Asia/Ho_Chi_Minh')) + datetime.timedelta(days=expires_in)
        }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_refresh_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Refresh token has expired",
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )
    except Exception as e:
        # Bắt tất cả các lỗi khác
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}",
        )


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Refresh token has expired",
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )
    except Exception as e:
        # Bắt tất cả các lỗi khác
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}",
        )


def verify_token(token: str) -> str | None:
    payload = decode_access_token(token)
    return payload.get('data', None)
