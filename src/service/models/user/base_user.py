from abc import ABC, abstractmethod
from pydantic import BaseModel
from datetime import datetime


class BaseUser(ABC, BaseModel):
    user_id: str
    username: str
    password: str
    email: str
    role: str = None
    is_online: bool = False
    created_at: datetime
    updated_at: datetime
