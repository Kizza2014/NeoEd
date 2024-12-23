from src.repository.mongodb.post import  PostRepository
from fastapi import APIRouter, Depends, HTTPException
from src.configs.connections.mongodb import get_mongo_connection
from typing import List
from src.service.models import PostResponse, PostCreate, PostUpdate
from pymongo.errors import PyMongoError


POST_CONTROLLER = APIRouter()


@POST_CONTROLLER.get("/classroom/{class_id}/post/all", response_model=List[PostResponse])
async def get_all_posts(class_id: str, connection=Depends(get_mongo_connection)):
    try:
        repo = PostRepository(connection)
        posts = await repo.get_posts_in_class(class_id)
        return [PostResponse(**post) for post in posts]
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")

@POST_CONTROLLER.get("/classroom/{class_id}/post/{post_id}/detail", response_model=PostResponse)
async def get_post_by_id(class_id: str, post_id: str, connection=Depends(get_mongo_connection)):
    try:
        repo = PostRepository(connection)
        post = await repo.get_post_by_id(class_id, post_id)
        if post is None:
            raise HTTPException(status_code=404, detail="Post not found")
        return PostResponse(**post)
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@POST_CONTROLLER.post("/classroom/{class_id}/post/create")
async def create_post(class_id: str, new_post: PostCreate, connection=Depends(get_mongo_connection)):
    try:
        repo = PostRepository(connection)
        status = await repo.create_post(class_id, new_post)
        if not status:
            raise HTTPException(status_code=500, detail='An unexpected error occurred. Create post failed')
        return {
            'message': 'Post created successfully',
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@POST_CONTROLLER.put("/classroom/{class_id}/post/{post_id}/update")
async def update_post(
        class_id: str,
        post_id: str,
        update_data: PostUpdate,
        connection=Depends(get_mongo_connection)
):
    try:
        repo = PostRepository(connection)
        status = await repo.update_post_by_id(class_id, post_id, update_data)
        if not status:
            raise HTTPException(status_code=500, detail='An unexpected error occurred. Update post failed')
        return {
            'message': 'Post updated successfully',
            'post_id': post_id,
            'update_info': update_data.model_dump(exclude_unset=True)
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@POST_CONTROLLER.delete("/classroom/{class_id}/post/{post_id}/delete")
async def delete_post(class_id: str, post_id: str, connection=Depends(get_mongo_connection)):
    try:
        repo = PostRepository(connection)
        status = await repo.delete_post_by_id(class_id, post_id)
        if not status:
            raise HTTPException(status_code=500, detail='An unexpected error occurred. Delete post failed')
        return {
            'message': 'Post deleted successfully',
            'post_id': post_id,
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")
