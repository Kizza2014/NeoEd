from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from config import MongoDBManager
from .book_controller import book_repository
from .user_controller import user_repository
from service import TransactionService
from repository import TransactionRepository


templates = Jinja2Templates(directory="static/templates")

transaction_repository = TransactionRepository(MongoDBManager.get_instance())
transaction_service = TransactionService(
    MongoDBManager.get_instance(),
    user_repository,
    book_repository,
    transaction_repository
)

transaction_controller = APIRouter()

@transaction_controller.post("/transaction/create", response_class=HTMLResponse)
async def perform_transaction(transaction_info: dict):
    transaction_service.book_transaction(transaction_info)








