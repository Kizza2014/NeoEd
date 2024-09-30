from fastapi import FastAPI, Query, HTTPException, Body
from starlette import status
from pymongo import MongoClient

from helper import is_valid_isbn
from models import *

# Database connection
CLIENT = MongoClient(
    'mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.1'
)
DB = CLIENT.get_database('test')
BOOKS_COLLECTION = DB.get_collection('books')
STUDENTS_COLLECTION = DB.get_collection('students')

app = FastAPI()


@app.get(
    "/books/",
    status_code=status.HTTP_200_OK,
    response_description="List all books",
    response_model=BooksContainer,
    response_model_by_alias=False,
)
async def read_all_books():
    return BooksContainer(books=BOOKS_COLLECTION.find().to_list())


@app.get(
    "/books/isbn/",
    status_code=status.HTTP_200_OK,
    response_model=BooksContainer
)
async def read_book(book_isbn: str = Query(min_length=10)):
    isbn_list = [x.strip() for x in book_isbn.split(',')]
    books_list = []

    for isbn in isbn_list:
        book = BOOKS_COLLECTION.find_one({'$text': {'$search': isbn}})
        if book is not None:
            books_list.append(book)

    if len(books_list) > 0:
        return BooksContainer(books=books_list)

    raise HTTPException(status_code=204, detail=f"Book {book_isbn} not found")


@app.get(
    "/books/year/",
    status_code=status.HTTP_200_OK,
    response_model=BooksContainer
)
async def read_book_by_publish_year(published_year: int = Query(gt=0, lt=9999)):
    books = BOOKS_COLLECTION.find({'published_year': published_year}).to_list()
    if books:
        return BooksContainer(books=books)

    raise HTTPException(status_code=404, detail="No book found")


@app.get(
    "/books/keywords/",
    status_code=status.HTTP_200_OK,
    response_model=BooksContainer,
    description="Type ISBN, keywords, author's name or categories"
)
def read_book_by_keyword(keywords: str = Query(min_length=1)):
    """
    Full-text search based on the below text indexes:
    db.books.createIndex({
        '_id': 'text',   # ISBN code of the book
        'title': 'text',
        'authors': 'text',
        'long_description': 'text',
        'short_description': 'text',
        'categories': 'text'
    },
    {
        weights: {
            '_id': 10,
            'title': 10,
            'authors': 10,
            'long_description': 5,
            'short_description': 5,
            'categories': 3
        }
    })
    """
    keywords_list = keywords.split(',')
    search = ["\"" + x.strip() + "\"" for x in keywords_list]
    search = ' '.join(search)
    res = BOOKS_COLLECTION.find({'$text': {'$search': search}}).to_list()

    if res:
        return BooksContainer(books=res)

    raise HTTPException(status_code=404, detail=f"No results for \"{keywords}\".")


@app.get(
    "/books/authors/",
    status_code=status.HTTP_200_OK,
    response_model=BooksContainer
)
def read_book_by_author(author: str):
    authors_list = author.split(',')
    search = ["\"" + x.strip() + "\"" for x in authors_list]
    search = ' '.join(search)
    res = BOOKS_COLLECTION.find({'$text': {'$search': search}}).to_list()

    if res:
        return BooksContainer(books=res)

    raise HTTPException(status_code=404, detail=f"No books found for author \"{author}\"")


@app.post(
    "/create-book",
    response_description="Add new book",
    response_model=BookModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_book(book_request: BookModel = Body(...)):
    isbn_set = {isbn['_id'] for isbn in BOOKS_COLLECTION.find({}, {'_id': 1}).to_list()}
    new_book = book_request.model_dump(by_alias=True)

    if is_valid_isbn(new_book['_id']):
        # check whether new_book['_id'] is exist or not
        if new_book['_id'] not in isbn_set:
            BOOKS_COLLECTION.insert_one(new_book)
            if BOOKS_COLLECTION.find_one({'_id': new_book['_id']}) is not None:
                return new_book

            raise HTTPException(status_code=304, detail="Book is not created")
        else:
            new_id = new_book['_id']
            raise HTTPException(status_code=302, detail=f'ISBN {new_id} already exists')

    raise HTTPException(status_code=406, detail="Invalid ISBN")


@app.delete(
    "/books/delete/",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=BookModel
)
async def delete_book(isbn: str):
    book = BOOKS_COLLECTION.find_one({'_id': isbn})

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    BOOKS_COLLECTION.delete_one({'_id': isbn})

    if BOOKS_COLLECTION.find_one({'_id': isbn}) is not None:
        raise HTTPException(status_code=304, detail="Book not deleted")

    return book
