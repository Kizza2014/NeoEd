from datetime import date
from pydantic import BaseModel
from typing import List, Optional


class UserCreate(BaseModel):
    id: str
    user_name: str
    gender: str
    birthdate: Optional[date] = None
    user_role: str
    address: Optional[str] = None
    email: Optional[str] = None
    user_passwd: str


class UserLogin(BaseModel):
    id: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    user_id: str
    roles: List[str]


class RegisterResponse(BaseModel):
    message: str
    user_id: str
