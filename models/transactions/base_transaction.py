from pydantic import BaseModel, Field
from typing import List


class BaseTransaction(BaseModel):
    id: str = Field(alias='_id')
    user_id: int
    amount: float
