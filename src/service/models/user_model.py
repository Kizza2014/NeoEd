from typing import Optional
from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, EmailStr


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
    username: str
    fullname: str
    gender: Gender
    birthdate: Optional[date] = None
    role: UserRole
    email: Optional[EmailStr] = None
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
    email: Optional[EmailStr] = None
    address: Optional[str] = None


class UserUpdateResponse(BaseModel):
    message: str
    username: str
    new_info: dict



class UserResponse(UserBase):
    joined_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserDeleteResponse(BaseModel):
    message: str
    username: str