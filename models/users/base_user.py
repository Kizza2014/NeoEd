from pydantic import BaseModel, Field
from typing import List
from ..books import BookContainer


class BaseUser(BaseModel):
    id: int = Field(alias="_id")
    name: str
    balance: float
    bought_books: BookContainer
    borrowed_books: BookContainer
    expired_books: BookContainer
