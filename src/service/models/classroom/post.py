from typing import Optional

from pydantic import BaseModel
from datetime import datetime


class PostBase(BaseModel):
    title: str
    author: str
    created_at: datetime
    updated_at: datetime
    content: str


class PostResponse(PostBase):
    id: str


class PostCreate(BaseModel):
    title: str
    author: str
    content: str


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
