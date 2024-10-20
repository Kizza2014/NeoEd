from datetime import datetime
from pydantic import BaseModel, Field
from typing import List


class BaseBook(BaseModel):
    id: str = Field(alias='_id')
    title: str
    authors: List[str]
    categories: List[str]
    status: str
    available_copies: int
    borrowed_copies: int
    rating: List[str]
    page_count: int
    published_yaer: int
    thumbnail_url: str
    short_description: str
    long_description: str
    lastUpdated: datetime
