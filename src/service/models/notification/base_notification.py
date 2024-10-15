from typing import List
from abc import ABC
from pydantic import BaseModel


class BaseNotification(ABC, BaseModel):
    notification_id: str
    title: str = None
    content: str = None
    created_at: str
    updated_at: str
    sender_id: str
    receiver_ids: List[str]
    is_read: bool = False
    