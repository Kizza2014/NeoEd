from abc import ABC
from pydantic import BaseModel


class BaseAttachment(ABC, BaseModel):
    classroom_item_id: str
    created_at: str
    attachment_type: str
