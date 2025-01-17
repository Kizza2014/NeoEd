import uuid
from typing import List
from abc import ABC
from pydantic import BaseModel
from datetime import datetime


class BaseNotification(ABC, BaseModel):
    notification_id: str = 'noti-' + str(uuid.uuid4())
    title: str = None
    content: str = None
    direct_url: str = None
    class_id: str
    created_at: datetime = datetime.now()
