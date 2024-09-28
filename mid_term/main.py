from datetime import datetime
from typing import Optional, List, Annotated
from fastapi import FastAPI, Path, Query, HTTPException, Body
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.functional_validators import BeforeValidator, AfterValidator
from starlette import status
from pymongo import MongoClient
from bson import ObjectId


CLIENT = MongoClient('mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.1')
DB = CLIENT.get_database('test')
BOOKS_COLLECTION = DB.get_collection('books')
STUDENTS_COLLECTION = DB.get_collection('students')

app = FastAPI()


class RatingModel(BaseModel):
    id: int
    student_id: int
    score: int
    reviews: str = Field(max_length=1000, default=None)


"""
Annotation to decode mongoDB Object id
"""
PyObjectId = Annotated[str, BeforeValidator(str)]

class BookModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str
    isbn: str
    authors: List[str]
    categories: List[str]
    status: str
    available_copies: int
    borrowed_copies: int
    ratings: List[RatingModel]
    page_count: int
    published_year: Optional[int] = None
    thumbnail_url: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "title": "This is a book",
                "isbn": "123456789012",
                "authors": "Nguyen Van A, Nguyen Thi B",
                "categories": {
                    "name": "This is a category",
                },
                "status": "Public",
                "available_copies": 10,
                "borrowed_copies": 0,
                "page_count": 400,
                "published_date": "2024-10-2",
                "thumbnail_url": 'https://s3.amazonaws.com/AKIAJC5RLADLUMVRPFDQ.book-thumb-images/ableson.jpg',
                "short_description": "This is a short description",
                "long_description": "This is a long description",
            }
        },
    )

class BooksContainer(BaseModel):
    """
    A container holding a list of `BookModel` instances.
    This exists because providing a top-level array in a JSON response can be a [vulnerability](https://haacked.com/archive/2009/06/25/json-hijacking.aspx/)
    """
    books: List[BookModel]

# class BookRequest(BaseModel):
#     id: Optional[int] = Field(description='ID is not needed on create', default=None)
#     isbn: str = Field(min_length=10, max_length=13)
#     title: str = Field(min_length=3)
#     published_date: str = Field(min_length=10)
#     thumbnail_url: Optional[str] = None
#     short_description: Optional[str] = Field(max_length=2500, default=None)
#     long_description: Optional[str] = Field(max_length=5000, default=None)
#     status: str = Field(max_length=10)
#     author: Optional[List[AuthorModel]] = None
#     rating: Optional[List[RatingModel]] = None
#     categories: Optional[List[str]] = None
#
#     model_config = {
#         "json_schema_extra": {
#             "example": {
#                 "title": "A new book",
#                 "author": "codingwithroby",
#                 "description": "A new description of a book",
#                 "rating": 5,
#                 'published_date': 2029
#             }
#         }
#     }

@app.get("/books", status_code=status.HTTP_200_OK,response_description="List all books",
         response_model=BooksContainer,
        response_model_by_alias=False,)
async def read_all_books():
    return BooksContainer(books= BOOKS_COLLECTION.find().to_list())


@app.get("/books/", status_code=status.HTTP_200_OK, response_model=BookModel)
async def read_book(book_isbn: str = Query(min_length=10, max_length=13)):
    if (
        book := BOOKS_COLLECTION.find_one({"isbn": book_isbn})
    ) is not None:
        return book

    raise HTTPException(status_code=204, detail=f"Book {book_isbn} not found")


@app.get("/books/publish/", status_code=status.HTTP_200_OK, response_model=BooksContainer)
async def read_book_by_publish_year(published_year: int = Query(gt=0, lt=9999)):
    return BooksContainer(books= BOOKS_COLLECTION.find({'published_year':published_year}).to_list())
    raise HTTPException(status_code=404, detail=f"No book found")



@app.get("/books/keywords/", status_code=status.HTTP_200_OK, response_model=BooksContainer)
def read_book_by_keyword(keywords: str = Query(min_length=1)):
    """
    Full-text search base on below text-indexes:
    db.books.createIndex({
                            'title':'text',
                            'long_description':'text',
                            'short_description':'text',
                            'long_description':'text',
                            'categories':'text'
                         },
                         {
                            weights:{
                                        'title':10,
                                        'long_description':5,
                                        'short_description':5,
                                        'categories':3
                                    }
                         })
    """
    return BooksContainer(books= BOOKS_COLLECTION.find({'$text': {'$search': keywords}}).to_list())
    raise HTTPException(status_code=404, detail=f"No results for {keywords}.")

# @app.post("/create-book", status_code=status.HTTP_201_CREATED, response_model=BookModel)
# async def create_book(book_request: BookRequest):
#     new_book = BookModel(**book_request.model_dump())
#     BOOKS.append(find_book_id(new_book))
#
#
# def find_book_id(book: BookModel):
#     book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
#     return book


# @app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
# async def update_book(book: BookRequest):
#     book_changed = False
#     for i in range(len(BOOKS)):
#         if BOOKS[i].id == book.id:
#             BOOKS[i] = book
#             book_changed = True
#     if not book_changed:
#         raise HTTPException(status_code=404, detail='Item not found')


# @app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_book(book_id: int = Path(gt=0)):
#     book_changed = False
#     for i in range(len(BOOKS)):
#         if BOOKS[i].id == book_id:
#             BOOKS.pop(i)
#             book_changed = True
#             break
#     if not book_changed:
#         raise HTTPException(status_code=404, detail='Item not found')