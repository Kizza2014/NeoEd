from src.repository.mysql import PostRepository
from fastapi import APIRouter, Depends
from src.configs.connections.mysql import get_mysql_conn
from typing import List
from src.service.models import Post


POST_CONTROLLER = APIRouter()


# @POST_CONTROLLER.get("/posts", response_model=List[Post])
# async def get_all(conn=Depends(get_mysql_conn)):
#     repo = PostRepository(conn)
#     return repo.get_all()
#
#
# @POST_CONTROLLER.get("/posts/{post_id}", response_model=Post)
# async def get_by_id(post_id: str, conn=Depends(get_mysql_conn)):
#     repo = PostRepository(conn)
#     return repo.get_by_id(post_id)
#
#
# @POST_CONTROLLER.put("/posts/{post_id}")
# async def update_by_id(post_id: str, new_item: Post, conn=Depends(get_mysql_conn)):
#     repo = PostRepository(conn)
#     if not repo.update_by_id(post_id, new_item):
#         return False
#     return new_item
#
#
# @POST_CONTROLLER.post("/posts")
# async def create(new_post: Post, conn=Depends(get_mysql_conn)):
#     repo = PostRepository(conn)
#     if not repo.insert(new_post):
#         return False
#     return new_post
#
#
# @POST_CONTROLLER.delete("/posts/{post_id}")
# async def delete_by_id(post_id: str, conn=Depends(get_mysql_conn)):
#     repo = PostRepository(conn)
#     return repo.delete_by_id(post_id)