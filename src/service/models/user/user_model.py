from typing import Optional
from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel


# Enums
class Gender(str, Enum):
    MALE = 'Male'
    FEMALE = 'Female'
    OTHER = 'Other'

class UserRole(str, Enum):
    TEACHER = 'Teacher'
    STUDENT = 'Student'
    ADMIN = 'Admin'


# Pydantic models for request/response
class UserBase(BaseModel):
    id: str
    username: str
    fullname: str
    gender: Gender
    birthdate: Optional[date] = None
    email: Optional[str] = None
    address: Optional[str] = None

class UserCreate(UserBase):
    password: str


class RegisterResponse(BaseModel):
    message: str
    username: str


class UserUpdate(BaseModel):
    fullname: Optional[str] = None
    gender: Optional[Gender] = None
    birthdate: Optional[date] = None
    email: Optional[str] = None
    address: Optional[str] = None


class UserResponse(UserBase):
    joined_at: Optional[datetime] = None

