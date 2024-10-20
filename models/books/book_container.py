from pydantic import BaseModel
from typing import List
from .base_book import BaseBook


class BookContainer(BaseModel):
    books: List[BaseBook]