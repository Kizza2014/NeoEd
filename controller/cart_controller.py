from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from config import MongoDBManager
from service import CartService
from .user_controller import user_repository
from .book_controller import book_repository


templates = Jinja2Templates(directory="static/templates")

cart_service = CartService(
    MongoDBManager.get_instance(),
    user_repository,
    book_repository
)

cart_controller = APIRouter()

@cart_controller.get("/cart", response_class=HTMLResponse)
async def get_cart(request: Request):
    cart = cart_service.get_cart(1)
    return templates.TemplateResponse(
        "cart_detail.html",
        {
            "request": request,
            "user_id": 1,
            "cart": cart["items"],
            "total_amount": cart["total_amount"]
        }
    )

@cart_controller.post("/cart")
async def add_to_cart(item: dict):
    cart_service.add_to_cart(item)





