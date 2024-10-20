from fastapi import APIRouter, Request
from repository import UserRepository
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from config import MongoDBManager
from service import CartService


default_user = {"id": 1, "name": "Zap"}

templates = Jinja2Templates(directory="static/templates")

user_repository = UserRepository(MongoDBManager.get_instance())
user_controller = APIRouter()

@user_controller.get("/user", response_class=HTMLResponse)
async def index(request: Request):
    user = user_repository.get_by_id(1)
    return templates.TemplateResponse("user_detail.html", {"request": request, "user": user})






