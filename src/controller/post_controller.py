from src.configs.connections.mysql import get_mysql_connection
from src.service.notification.notification_service import NotificationService
from src.repository.mysql.user import UserRepository
from src.repository.mongodb.post import PostRepository
from src.repository.mongodb.classroom import MongoClassroomRepository
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from src.configs.connections import get_mongo_connection
from typing import List
from src.service.models.classroom import PostResponse, PostCreate, PostUpdate
from pymongo.errors import PyMongoError
from src.configs.connections.blob_storage import SupabaseStorage
import uuid
from src.service.authentication.utils import verify_token


BUCKET = 'posts'
POST_CONTROLLER = APIRouter(tags=['Post'])


@POST_CONTROLLER.get("/classroom/{class_id}/post/all", response_model=List[PostResponse])
async def get_all_posts(
        class_id: str,
        user_id: str=Depends(verify_token),
        connection=Depends(get_mongo_connection)
) -> List[PostResponse]:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        # ensure user is a participant of the class
        classroom_repo = MongoClassroomRepository(connection)
        post_repo = PostRepository(connection)
        if not await classroom_repo.find_participant_in_class(user_id, class_id):
            raise HTTPException(status_code=403, detail='Unauthorized. You must be a participant of the class.')

        posts = await post_repo.get_posts_in_class(class_id)
        return [PostResponse(**post) for post in posts]
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@POST_CONTROLLER.get("/classroom/{class_id}/post/{post_id}/detail", response_model=PostResponse)
async def get_post_by_id(
        class_id: str,
        post_id: str,
        user_id: str=Depends(verify_token),
        connection=Depends(get_mongo_connection)
) -> PostResponse:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        # ensure user is a participant of the class
        classroom_repo = MongoClassroomRepository(connection)
        if not await classroom_repo.find_participant_in_class(user_id, class_id):
            raise HTTPException(status_code=403, detail='Unauthorized. You must be a participant of the class.')

        post_repo = PostRepository(connection)
        db_post = await post_repo.get_post_by_id(class_id, post_id)
        if db_post is None:
            raise HTTPException(status_code=404, detail="Post not found")

        # generate url for each attachment
        storage = SupabaseStorage()
        post_folder = class_id + '/' + post_id
        urls = await storage.get_file_urls(
            bucket_name=BUCKET,
            file_locations=[post_folder + '/' + file['filename'] for file in db_post['attachments']]
        )
        db_post['attachments'] = urls

        return PostResponse(**db_post)
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@POST_CONTROLLER.post("/classroom/{class_id}/post/create")
async def create_post(
        class_id: str,
        user_id: str=Depends(verify_token),
        title: str = Form(...),
        content: str = Form(...),
        attachments: List[UploadFile] = File(None),
        connection=Depends(get_mongo_connection),
        mysql_cnx=Depends(get_mysql_connection)
) -> dict:

    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        # ensure user is a participant of the class
        classroom_repo = MongoClassroomRepository(connection)
        if not await classroom_repo.find_participant_in_class(user_id, class_id):
            raise HTTPException(status_code=403, detail='Unauthorized. You must be a participant of the class.')

        user_repo = UserRepository(mysql_cnx)
        current_user = await user_repo.get_by_id(user_id)

        # create post in database
        repo = PostRepository(connection)
        post_dict = {
            "title": title,
            "content": content,
            "attachments": [{'filename': file.filename} for file in attachments] if attachments else None
        }
        post_dict = {k: v for k, v in post_dict.items() if v is not None}
        newpost_id = 'post-' + str(uuid.uuid4())
        new_post = PostCreate(**post_dict, id=newpost_id, author=current_user['username'])
        if not await repo.create_post(class_id=class_id, new_post=new_post):
            raise HTTPException(status_code=500, detail='An unexpected error occurred. Create post failed')

        # upload attachments to storage
        storage = SupabaseStorage()
        post_folder = class_id + "/" + newpost_id
        upload_results = await storage.bulk_upload(
            bucket_name=BUCKET,
            files=attachments if attachments else [],
            dest_folder=post_folder
        )

        # create notification for students
        notification_service = NotificationService(class_id, mysql_cnx)
        notification_service.create_new_notification_for_students(
            title=current_user['username'] + " has created a new post.",
            content=title,
            direct_url=f"/c/{class_id}/p/{newpost_id}"
        )

        return {
            'message': 'Post created successfully',
            'post_id': newpost_id,
            'upload_results': upload_results,
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@POST_CONTROLLER.patch("/classroom/{class_id}/post/{post_id}/update")
async def update_post(
        class_id: str,
        post_id: str,
        user_id: str=Depends(verify_token),
        title: str = Form(None),
        content: str = Form(None),
        additional_attachments: List[UploadFile] = File(None),
        removal_attachments: List[str] = Form(None),
        mysql_connection=Depends(get_mysql_connection),
        mongo_connection=Depends(get_mongo_connection),
) -> dict:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        user_repo = UserRepository(mysql_connection)
        current_user = await user_repo.get_by_id(user_id)

        # ensure user is post's author
        repo = PostRepository(mongo_connection)
        db_post = await repo.get_post_by_id(class_id, post_id)
        if current_user['username'] != db_post['author']:
            raise HTTPException(status_code=403, detail='Unauthorized. You must be the author of the post.')

        # update post in database
        update_data_dict = {
            "title": title if title else None,
            "content": content if content else None,
            "additional_attachments": [{'filename': file.filename} for file in
                                       additional_attachments] if additional_attachments else None,
            "removal_attachments": [{'filename': filename} for filename in removal_attachments] if removal_attachments else None
        }
        update_data_dict = {k: v for k, v in update_data_dict.items() if v is not None}

        update_data = PostUpdate(**update_data_dict)
        status = await repo.update_by_id(class_id, post_id, update_data)
        if not status:
            raise HTTPException(status_code=500, detail='An unexpected error occurred. Update post failed')

        # upload and remove attachments
        post_folder = class_id + '/' + post_id
        storage = SupabaseStorage()
        upload_results = await storage.bulk_upload(
            bucket_name=BUCKET,
            files=additional_attachments if additional_attachments else [],
            dest_folder=post_folder
        )

        remove_results = await storage.remove_files(
            bucket_name=BUCKET,
            file_locations=[post_folder + '/' + filename for filename in removal_attachments]
            if removal_attachments else []
        )

        return {
            'message': 'Post updated successfully',
            'post_id': post_id,
            'update_info': update_data.model_dump(exclude_unset=True),
            'upload_results': upload_results if additional_attachments else None,
            'remove_results': remove_results if removal_attachments else None
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@POST_CONTROLLER.delete("/classroom/{class_id}/post/{post_id}/delete")
async def delete_post(
        class_id: str,
        post_id: str,
        user_id: str=Depends(verify_token),
        mysql_connection=Depends(get_mysql_connection),
        mongo_connection=Depends(get_mongo_connection)
) -> dict:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        user_repo = UserRepository(mysql_connection)
        current_user = await user_repo.get_by_id(user_id)

        # ensure user is post's author
        repo = PostRepository(mongo_connection)
        db_post = await repo.get_post_by_id(class_id, post_id)
        if current_user['username'] != db_post['author']:
            raise HTTPException(status_code=403, detail='Unauthorized. You must be the author of the post.')

        # delete post in database
        repo = PostRepository(mongo_connection)
        status = await repo.delete_by_id(class_id, post_id)
        if not status:
            raise HTTPException(status_code=500, detail='An unexpected error occurred. Delete post failed')

        # delete attachments in storage
        storage = SupabaseStorage()
        post_folder = class_id +'/' + post_id
        remove_results = await storage.remove_files(
            bucket_name=BUCKET,
            file_locations=[post_folder + '/' + file['filename'] for file in db_post['attachments']]
        )

        return {
            'message': 'Post deleted successfully',
            'post_id': post_id,
            'remove_results': remove_results
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")

