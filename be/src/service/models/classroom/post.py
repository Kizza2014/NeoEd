from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class PostBase(BaseModel):
    title: str
    author: str
    created_at: datetime
    updated_at: datetime
    content: str
    attachments: Optional[List[dict]] = None


class PostResponse(PostBase):
    id: str


class PostCreate(BaseModel):
    id: str
    title: str
    author: str
    content: str
    attachments: Optional[List[dict]] = None


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    additional_attachments: Optional[List[dict]] = None
    removal_attachments: Optional[List[dict]] = None
