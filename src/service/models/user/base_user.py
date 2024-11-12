from abc import ABC
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class BaseUser(ABC, BaseModel):
    id: str
    user_name: str
    gender: str
    birthdate: Optional[date] = None
    user_role: str
    address: Optional[str] = None
    email: Optional[str] = None
    user_passwd: str
    joined_at: Optional[datetime] = None
    is_online: bool = False

