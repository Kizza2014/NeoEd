from fastapi import APIRouter, Request, Form, Query
from repository import BookRepository
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from config import MongoDBManager


default_user = {"id": 1, "name": "Zap"}
default_cart = [
    {"name": "Book 1", "price": 100, "quantity": 1},
    {"name": "Book 2", "price": 150, "quantity": 2}
]

templates = Jinja2Templates(directory="static/templates")
book_repository = BookRepository(MongoDBManager.get_instance())
book_controller = APIRouter()

@book_controller.get("/", response_class=HTMLResponse)
async def index(request: Request):
    books = book_repository.get_all()
    return templates.TemplateResponse("index.html", {"request": request, "books": books})

@book_controller.get("/search/")
def get_book_by_keyword(request: Request, keywords: str = Query(min_length=1)):
    books = book_repository.get_by_keyword(keywords)
    return templates.TemplateResponse("index.html", {"request": request, "books": books})

@book_controller.get("/book/{book_id}", response_class=HTMLResponse)
async def get_book(request: Request, book_id: str):
    book = book_repository.get_by_id(book_id)
    if book:
        return templates.TemplateResponse("book_detail.html", {"request": request, "book": book, "user": default_user, "cart": default_cart})
    return {"message": "Không tìm thấy sách"}


@book_controller.post("/add")
async def add_book(title: str = Form(...), author: str = Form(...), year: int = Form(...)):
    new_book = {'title': title, 'author': author, 'year': year}
    book_repository.insert(new_book)
    return {"message": "Sách đã được thêm thành công"}


@book_controller.post("/edit/{book_id}")
async def update_book(book_id: str, title: str = Form(...), author: str = Form(...), year: int = Form(...)):
    updated_data = {"title": title, "author": author, "year": year}
    updated_book = book_repository.update_by_id(book_id, updated_data)
    if updated_book:
        return {"message": "Sách đã được cập nhật"}
    return {"message": "Cập nhật thất bại"}

@book_controller.get("/delete/{book_id}")
async def delete_book(book_id: str):
    result = book_repository.delete_by_id(book_id)
    if result:
        return {"message": "Sách đã được xóa"}
    return {"message": "Xóa sách thất bại"}