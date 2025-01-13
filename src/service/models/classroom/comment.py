from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Comment(BaseModel):
    id: str
    user_id: str
    username: str
    content: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
