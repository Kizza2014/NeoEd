from src.repository.mysql import UserRepository
from fastapi import APIRouter, Depends
from src.configs.connections.mysql import get_connection
from typing import List
from src.service.models import BaseUser


USER_CONTROLLER = APIRouter()


@USER_CONTROLLER.get("/users", response_model=List[BaseUser])
async def get_all(conn=Depends(get_connection)):
    repo = UserRepository(conn)
    return repo.get_all()


@USER_CONTROLLER.get("/users/{user_id}", response_model=BaseUser)
async def get_by_id(user_id: str, conn=Depends(get_connection)):
    repo = UserRepository(conn)
    return repo.get_by_id(user_id)


@USER_CONTROLLER.put("/users/{user_id}")
async def update_by_id(user_id: str, new_item: BaseUser, conn=Depends(get_connection)):
    repo = UserRepository(conn)
    if not repo.update_by_id(user_id, new_item):
        return False
    return new_item


@USER_CONTROLLER.post("/users")
async def create(new_user: BaseUser, conn=Depends(get_connection)):
    repo = UserRepository(conn)
    if not repo.insert(new_user):
        return False
    return new_user


@USER_CONTROLLER.delete("/users/{user_id}")
async def delete_by_id(user_id: str, conn=Depends(get_connection)):
    repo = UserRepository(conn)
    return repo.delete_by_id(user_id)