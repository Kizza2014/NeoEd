import jwt
import datetime

from fastapi.security import HTTPBearer
from passlib.context import CryptContext

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
        'exp': datetime.datetime.now() + datetime.timedelta(minutes=expires_in)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data, expires_in=7) -> str:
    payload = {
        "data": data,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=expires_in)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
