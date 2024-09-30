from pydantic import BaseModel, Field, ConfigDict
from pydantic.functional_validators import BeforeValidator
from typing import Optional, List, Annotated
from bson import ObjectId

class RatingModel(BaseModel):
    id: int
    student_id: int
    score: int
    reviews: str = Field(max_length=1000, default=None)


# Annotation to decode mongoDB Object id
PyObjectId = Annotated[str, BeforeValidator(str)]

class BookModel(BaseModel):
    id: str = Field(alias="_id", default=None)
    title: str
    authors: List[str]
    categories: List[str]
    status: str
    available_copies: int
    borrowed_copies: int
    ratings: List[RatingModel]
    page_count: Optional[int] = None
    published_year: Optional[int] = None
    thumbnail_url: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "_id": "0123456789",
                "title": "This is a book",
                "authors": ["Nguyen Van A", "Nguyen Thi B"],
                "categories": ["category A", "category B"],
                "status": "Publish",
                "available_copies": 10,
                "borrowed_copies": 0,
                "page_count": 400,
                "published_year": "2020",
                "thumbnail_url": '/home/..../thumbnail/image.jpg',
                "short_description": "This is a short description",
                "long_description": "This is a long description",
                "ratings": []
            }
        },
    )

class BooksContainer(BaseModel):
    """
    A container holding a list of `BookModel` instances.
    This exists because providing a top-level array in a JSON response can be a [vulnerability](https://haacked.com/archive/2009/06/25/json-hijacking.aspx/)
    """
    books: List[BookModel]


class BookRequest(BaseModel):
    id: str = Field(alias='_id')
    title: str = Field(min_length=3)
    authors: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    status: str
    available_copies: int
    borrowed_copies: int
    ratings: None
    page_count: Optional[int] = None
    published_year: Optional[int] = None
    thumbnail_url: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "codingwithroby",
                "description": "A new description of a book",
                "rating": 5,
                'published_date': 2029
            }
        }
    }
