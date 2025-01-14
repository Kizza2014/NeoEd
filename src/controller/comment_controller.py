from fastapi import APIRouter, Depends, HTTPException, Form
from pytz import timezone
from src.service.authentication.utils import verify_token
from src.controller.utils import get_mongo_repo, get_mysql_repo
from src.configs.connections.mongodb import get_mongo_connection
from src.configs.connections.mysql import get_mysql_connection
from typing import List
from src.service.models.classroom import Comment
from pymongo.errors import PyMongoError
import uuid


COMMENT_CONTROLLER = APIRouter(tags=['Comment'])
TIMEZONE = timezone('Asia/Ho_Chi_Minh')


@COMMENT_CONTROLLER.get('/classroom/{class_id/post/{post_id}/comment/all')
async def get_comments_of_post(
        class_id: str,
        post_id: str,
        user_id: str=Depends(verify_token),
        mongo_cnx=Depends(get_mongo_connection)
):
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        repo = await get_mongo_repo(mongo_cnx)

        # ensure user is a participant of the class
        if not await repo['classroom'].find_participant_in_class(user_id, class_id):
            raise HTTPException(status_code=403, detail='You are not a participant of this class.')

        comments = await repo['comment'].get_all(class_id, post_id)
        if comments is None:
            raise HTTPException(status_code=404, detail='Classroom or post not found.')
        return [Comment(**comment) for comment in comments]
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@COMMENT_CONTROLLER.get('/classroom/{class_id/assignment/{assgn_id}/comment/all', response_model=List[Comment])
async def get_comments_of_assignment(
        class_id: str,
        assgn_id: str,
        user_id: str = Depends(verify_token),
        mongo_cnx=Depends(get_mongo_connection)
) -> List[Comment]:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        repo = await get_mongo_repo(mongo_cnx)

        # ensure user is a participant of the class
        if not await repo['classroom'].find_participant_in_class(user_id, class_id):
            raise HTTPException(status_code=403, detail='Forbidden. You are not a participant of this class.')

        comments = await repo['comment'].get_all(class_id, assgn_id)
        if comments is None:
            raise HTTPException(status_code=404, detail='Classroom or assignment not found.')

        return [Comment(**comment) for comment in comments]
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@COMMENT_CONTROLLER.post('/classroom/{class_id}/post/{post_id}/comment/create', response_model=dict)
async def create_post_comment(
        class_id: str,
        post_id: str,
        user_id: str=Depends(verify_token),
        content: str=Form(...),
        mysql_connection=Depends(get_mysql_connection),
        mongo_cnx=Depends(get_mongo_connection)
) -> dict:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        mysql_repo = await get_mysql_repo(mysql_connection)
        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure user is a participant of the class
        if not await mongo_repo['classroom'].find_participant_in_class(user_id, class_id):
            raise HTTPException(status_code=403, detail='You are not a participant of this class.')

        # create comment
        current_user = await mysql_repo['user'].get_by_id(user_id)
        comment_id = 'comment-' + str(uuid.uuid4())
        comment = Comment(id=comment_id, user_id=user_id, username=current_user['username'], content=content)
        if not await mongo_repo['comment'].create_comment(class_id, post_id, comment):
            raise HTTPException(status_code=500, detail='Unexpected error occurred. Create comment failed.')

        return {
            'message': 'Comment created successfully',
            'comment_id': comment_id
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@COMMENT_CONTROLLER.post('/classroom/{class_id}/assignment/{assgn_id}/comment/create', response_model=dict)
async def create_assignment_comment(
        class_id: str,
        assgn_id: str,
        user_id: str = Depends(verify_token),
        content: str = Form(...),
        mysql_connection=Depends(get_mysql_connection),
        mongo_cnx=Depends(get_mongo_connection)
) -> dict:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        mysql_repo = await get_mysql_repo(mysql_connection)
        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure user is a participant of the class
        if not await mongo_repo['classroom'].find_participant_in_class(user_id, class_id):
            raise HTTPException(status_code=403, detail='You are not a participant of this class.')

        # create comment
        current_user = await mysql_repo['user'].get_by_id(user_id)
        comment_id = 'comment-' + str(uuid.uuid4())
        comment = Comment(id=comment_id, user_id=user_id, username=current_user['username'], content=content)
        if not await mongo_repo['comment'].create_comment(class_id, assgn_id, comment):
            raise HTTPException(status_code=500, detail='Unexpected error occurred. Create comment failed.')

        return {
            'message': 'Comment created successfully',
            'comment_id': comment_id
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@COMMENT_CONTROLLER.put('/classroom/{class_id}/post/{post_id}/comment/{comment_id}/update', response_model=dict)
async def update_post_comment(
        class_id: str,
        post_id: str,
        comment_id: str,
        user_id: str = Depends(verify_token),
        content: str = Form(...),
        mongo_cnx=Depends(get_mongo_connection)
) -> dict:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure user is a participant of the class
        if not await mongo_repo['classroom'].find_participant_in_class(user_id, class_id):
            raise HTTPException(status_code=403, detail='Forbidden. You are not a participant of this class.')

        # ensure user is the author of the comment
        db_comment = await mongo_repo['comment'].get_by_id(class_id, post_id, comment_id)
        if db_comment['user_id'] != user_id:
            raise HTTPException(status_code=403, detail='Forbidden. You are not the author of this comment.')

        # update comment
        if not await mongo_repo['comment'].update_comment(class_id, post_id, comment_id, content):
            raise HTTPException(status_code=500, detail='Unexpected error occurred. Update comment failed.')
        return {
            'message': 'Comment updated successfully',
            'comment_id': comment_id
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@COMMENT_CONTROLLER.put('/classroom/{class_id}/assignment/{assgn_id}/comment/{comment_id}/update', response_model=dict)
async def update_assignment_comment(
        class_id: str,
        assgn_id: str,
        comment_id: str,
        user_id: str = Depends(verify_token),
        content: str = Form(...),
        mongo_cnx=Depends(get_mongo_connection)
) -> dict:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure user is a participant of the class
        if not await mongo_repo['classroom'].find_participant_in_class(user_id, class_id):
            raise HTTPException(status_code=403, detail='Forbidden. You are not a participant of this class.')

        # ensure user is the author of the comment
        db_comment = await mongo_repo['comment'].get_by_id(class_id, assgn_id, comment_id)
        if db_comment['user_id'] != user_id:
            raise HTTPException(status_code=403, detail='Forbidden. You are not the author of this comment.')

        # update comment
        if not await mongo_repo['comment'].update_comment(class_id, assgn_id, comment_id, content):
            raise HTTPException(status_code=500, detail='Unexpected error occurred. Update comment failed.')
        return {
            'message': 'Comment updated successfully',
            'comment_id': comment_id
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@COMMENT_CONTROLLER.delete('/classroom/{class_id}/post/{post_id}/comment/{comment_id}/delete', response_model=dict)
async def delete_post_comment(
        class_id: str,
        post_id: str,
        comment_id: str,
        user_id: str=Depends(verify_token),
        mongo_cnx=Depends(get_mongo_connection)
):
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure user is a participant of the class
        if not await mongo_repo['classroom'].find_participant_in_class(user_id, class_id):
            raise HTTPException(status_code=403, detail='Forbidden. You are not a participant of this class.')

        # ensure user is the author of the comment
        db_comment = await mongo_repo['comment'].get_by_id(class_id, post_id, comment_id)
        if db_comment['user_id'] != user_id:
            raise HTTPException(status_code=403, detail='Forbidden. You are not the author of this comment.')

        # delete comment
        if not await mongo_repo['comment'].delete_comment(class_id, post_id, comment_id):
            raise HTTPException(status_code=500, detail='Unexpected error occurred. Delete comment failed.')
        return {
            'message': 'Comment deleted successfully',
            'comment_id': comment_id
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@COMMENT_CONTROLLER.delete('/classroom/{class_id}/assignment/{assgn_id}/comment/{comment_id}/delete', response_model=dict)
async def delete_assignment_comment(
        class_id: str,
        assgn_id: str,
        comment_id: str,
        user_id: str=Depends(verify_token),
        mongo_cnx=Depends(get_mongo_connection)
):
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure user is a participant of the class
        if not await mongo_repo['classroom'].find_participant_in_class(user_id, class_id):
            raise HTTPException(status_code=403, detail='Forbidden. You are not a participant of this class.')

        # ensure user is the author of the comment
        db_comment = await mongo_repo['comment'].get_by_id(class_id, assgn_id, comment_id)
        if db_comment['user_id'] != user_id:
            raise HTTPException(status_code=403, detail='Forbidden. You are not the author of this comment.')

        # delete comment
        if not await mongo_repo['comment'].delete_comment(class_id, assgn_id, comment_id):
            raise HTTPException(status_code=500, detail='Unexpected error occurred. Delete comment failed.')
        return {
            'message': 'Comment deleted successfully',
            'comment_id': comment_id
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")

