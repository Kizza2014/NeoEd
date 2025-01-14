from src.service.models.exceptions import ClassroomNotFoundException
from src.configs.connections.mysql import get_mysql_connection
from src.service.notification.notification_service import NotificationService
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from src.configs.connections import get_mongo_connection
from typing import List
from src.service.models.classroom import PostResponse, PostCreate, PostUpdate
from pymongo.errors import PyMongoError
from src.configs.connections.blob_storage import SupabaseStorage
import uuid
from src.service.authentication.utils import verify_token
from src.controller.utils import get_mongo_repo, get_mysql_repo


BUCKET = 'posts'
POST_CONTROLLER = APIRouter(tags=['Post'])


@POST_CONTROLLER.get("/classroom/{class_id}/post/all", response_model=List[PostResponse])
async def get_all_posts(
        class_id: str,
        user_id: str=Depends(verify_token),
        mongo_cnx=Depends(get_mongo_connection)
) -> List[PostResponse]:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure user is a participant of the class
        if not await mongo_repo['classroom'].find_participant_in_class(user_id, class_id):
            raise HTTPException(status_code=403, detail='Unauthorized. You must be a participant of the class.')

        posts = await mongo_repo['post'].get_posts_in_class(class_id)
        if posts is None:
            raise HTTPException(status_code=404, detail='Class not found.')
        return [PostResponse(**post) for post in posts]
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")
    except ClassroomNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@POST_CONTROLLER.get("/classroom/{class_id}/post/{post_id}/detail", response_model=PostResponse)
async def get_post_by_id(
        class_id: str,
        post_id: str,
        user_id: str=Depends(verify_token),
        mongo_cnx=Depends(get_mongo_connection)
) -> PostResponse:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure user is a participant of the class
        if not await mongo_repo['classroom'].find_participant_in_class(user_id, class_id):
            raise HTTPException(status_code=403, detail='Unauthorized. You must be a participant of the class.')

        db_post = await mongo_repo['post'].get_by_id(class_id, post_id)
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
        mongo_cnx=Depends(get_mongo_connection),
        mysql_cnx=Depends(get_mysql_connection)
) -> dict:

    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        mysql_repo = await get_mysql_repo(mysql_cnx, auto_commit=False)
        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure user is a participant of the class
        if not await mongo_repo['classroom'].find_participant_in_class(user_id, class_id):
            raise HTTPException(status_code=403, detail='Unauthorized. You must be a participant of the class.')

        # create post in database
        post_dict = {
            "title": title,
            "content": content,
            "attachments": [{'filename': file.filename} for file in attachments] if attachments else None
        }
        post_dict = {k: v for k, v in post_dict.items() if v is not None}
        newpost_id = 'post-' + str(uuid.uuid4())
        current_user = await mysql_repo['user'].get_by_id(user_id)
        new_post = PostCreate(**post_dict, id=newpost_id, author=current_user['username'])
        if not await mongo_repo['post'].create_post(class_id=class_id, new_post=new_post):
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


@POST_CONTROLLER.put("/classroom/{class_id}/post/{post_id}/update")
async def update_post(
        class_id: str,
        post_id: str,
        user_id: str=Depends(verify_token),
        title: str = Form(None),
        content: str = Form(None),
        additional_attachments: List[UploadFile] = File(None),
        removal_attachments: List[str] = Form(None),
        mysql_cnx=Depends(get_mysql_connection),
        mongo_cnx=Depends(get_mongo_connection),
) -> dict:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        mysql_repo = await get_mysql_repo(mysql_cnx)
        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure user is post's author
        current_user = await mysql_repo['user'].get_by_id(user_id)
        db_post = await mongo_repo['post'].get_by_id(class_id, post_id)
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
        status = await mongo_repo['post'].update_by_id(class_id, post_id, update_data)
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
        mysql_cnx=Depends(get_mysql_connection),
        mongo_cnx=Depends(get_mongo_connection)
) -> dict:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        mysql_repo = await get_mysql_repo(mysql_cnx)
        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure user is post's author or class owner
        current_user = await mysql_repo['user'].get_by_id(user_id)
        db_post = await mongo_repo['post'].get_by_id(class_id, post_id)
        class_owner = await mysql_repo['classroom'].get_owner(class_id)
        if current_user['username'] != db_post['author'] and user_id != class_owner['id']:
            raise HTTPException(status_code=403, detail='Unauthorized. You must be the author of the post or class owner.')

        # delete post in database
        status = await mongo_repo['post'].delete_by_id(class_id, post_id)
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

