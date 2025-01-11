from fastapi import APIRouter, Depends
from src.configs.connections.mysql import get_mysql_connection
from src.configs.connections.mongodb import get_mongo_connection
from src.service.models.classroom import ClassroomCreate, ClassroomUpdate, ClassroomResponse
from mysql.connector import Error as MySQLError
from pymongo.errors import PyMongoError
from fastapi import Form, HTTPException
import uuid
from src.service.authentication.utils import *
from src.controller.utils import get_mysql_repo, handle_transaction, get_mongo_repo, role_in_classroom, MySQLRepo


CLASSROOM_CONTROLLER = APIRouter(tags=['Classroom'])


async def is_classroom_owner(user_id: str, class_id: str, mysql_repo: MySQLRepo) -> bool:
    owner = await mysql_repo['classroom'].get_owner(class_id)
    return user_id == owner['id']


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                                        CLASSROOM GENERAL API
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

@CLASSROOM_CONTROLLER.get("/classroom/all", response_model=dict)
async def get_my_classrooms(
        user_id: str = Depends(verify_token),
        mysql_cnx=Depends(get_mysql_connection)
) -> dict:
    try:
        if not user_id:
            raise HTTPException(status_code=403, detail='Unauthorized. Try to login again before accessing this resource.')

        mysql_repo = await get_mysql_repo(mysql_cnx=mysql_cnx)
        classrooms = await mysql_repo['classroom'].get_classroom_for_user(user_id)
        return classrooms
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")


@CLASSROOM_CONTROLLER.get("/classroom/{class_id}/detail", response_model=ClassroomResponse)
async def get_by_id(class_id: str, mysql_cnx=Depends(get_mysql_connection)) -> ClassroomResponse:
    try:
        mysql_repo = await get_mysql_repo(mysql_cnx=mysql_cnx)
        db_classroom = await mysql_repo['classroom'].get_by_id(class_id)
        if not db_classroom:
            raise HTTPException(status_code=404, detail="Classroom not found")
        return ClassroomResponse(**db_classroom)
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@CLASSROOM_CONTROLLER.post("/classroom/create", response_model=dict)
async def create_classroom(
        user_id: str=Depends(verify_token),
        class_name: str = Form(...),
        subject_name: str = Form(...),
        class_schedule: str = Form(None),
        description: str = Form(None),
        mysql_cnx=Depends(get_mysql_connection),
        mongo_cnx=Depends(get_mongo_connection)
) -> dict:
    try:
        if not user_id:
            raise HTTPException(status_code=403, detail='Unauthorized. Try to login again before accessing this resource.')

        mysql_repo = await get_mysql_repo(mysql_cnx, auto_commit=False)
        mongo_repo = await get_mongo_repo(mongo_cnx)

        # create classroom
        current_user = await mysql_repo['user'].get_by_id(user_id)
        information = {
            'class_name': class_name,
            'subject_name': subject_name,
            'class_schedule': class_schedule if class_schedule else None,
            'description': description if description else None,
            'owner_id': current_user['id'],
            'owner_username': current_user['username'],
            'owner_fullname': current_user['fullname'],
        }
        information = {k: v for k, v in information.items() if v is not None}
        class_id = 'classroom-' + str(uuid.uuid4())
        new_classroom = ClassroomCreate(**information, id=class_id)

        # transaction-like operation
        status1 = await mysql_repo['classroom'].create_classroom(new_classroom)
        status2 = await mongo_repo['classroom'].create_classroom(new_classroom)
        await handle_transaction([status1, status2], mysql_cnx)

        return {
            'message': f'Created classroom successfully',
            'class_id': class_id,
        }
    except MySQLError as e:
        mysql_cnx.rollback()
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")
    except PyMongoError as e:
        mysql_cnx.rollback()
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@CLASSROOM_CONTROLLER.get('/classroom/{class_id}/participant/all')
async def get_all_participants(class_id: str, mongo_cnx=Depends(get_mongo_connection)) -> dict:
    try:
        mongo_repo = await get_mongo_repo(mongo_cnx)
        return await mongo_repo['classroom'].get_all_participants(class_id)
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@CLASSROOM_CONTROLLER.put('/classroom/join', response_model=dict)
async def join_classroom(
        invitation_code: str,
        user_id: str=Depends(verify_token),
        mysql_cnx=Depends(get_mysql_connection),
        mongo_cnx=Depends(get_mongo_connection)
) -> dict:
    """
    For student to join into classroom
    """
    try:
        if not user_id:
            raise HTTPException(status_code=403, detail='Unauthorized. Try to login again before accessing this resource.')

        mysql_repo = await get_mysql_repo(mysql_cnx, auto_commit=False)
        mongo_repo = await get_mongo_repo(mongo_cnx)

        db_class = await mysql_repo['classroom'].get_by_invitation_code(invitation_code)
        class_id = db_class['id']

        # verify user is not already in classroom
        if await mongo_repo['classroom'].find_participant_in_class(user_id, class_id):
            raise HTTPException(status_code=403, detail='Forbidden. You are already in this classroom')

        # add participant
        current_user = await mysql_repo['user'].get_by_id(user_id)
        status1 = await mysql_repo['classroom'].add_participant(current_user['id'], class_id, role='student')
        status2 = await mongo_repo['classroom'].add_participant(current_user['id'], current_user['username'], class_id, role='student')
        await handle_transaction([status1, status2], mysql_cnx)

        return {
            'message': 'Joined classroom successfully',
            'class_id': class_id,
        }
    except MySQLError as e:
        mysql_cnx.rollback()
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")
    except PyMongoError as e:
        mysql_cnx.rollback()
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@CLASSROOM_CONTROLLER.delete('/classroom/{class_id}/participant/leave', response_model=dict)
async def leave_classroom(
        class_id: str,
        user_id: str=Depends(verify_token),
        mysql_cnx=Depends(get_mysql_connection),
        mongo_cnx=Depends(get_mongo_connection)
) -> dict:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        mysql_repo = await get_mysql_repo(mysql_cnx, auto_commit=False)
        mongo_repo = await get_mongo_repo(mongo_cnx)

        # when user is classroom's owner
        if await is_classroom_owner(user_id, class_id, mysql_repo):
            raise HTTPException(status_code=403, detail='Forbidden. Owner cannot leave classroom')

        # remove participant
        user_role = await role_in_classroom(user_id, class_id, mysql_repo)
        status1 = await mysql_repo['classroom'].remove_participant(user_id, class_id, role=user_role)
        status2 = await mongo_repo['classroom'].remove_participant(user_id, class_id, role=user_role)
        await handle_transaction([status1, status2], mysql_cnx)

        return {
            'message': 'Left classroom successfully',
            'class_id': class_id,
        }
    except MySQLError as e:
        mysql_cnx.rollback()
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")
    except PyMongoError as e:
        mysql_cnx.rollback()
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                                        CLASSROOM TEACHER API
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

@CLASSROOM_CONTROLLER.get("/classroom/{class_id}/invitation-code", response_model=str)
async def get_invitation_code(
        class_id: str,
        user_id=Depends(verify_token),
        mysql_cnx=Depends(get_mysql_connection)
):
    try:
        if not user_id:
            raise HTTPException(status_code=403, detail='Unauthorized. Try to login again before accessing this resource.')

        mysql_repo = await get_mysql_repo(mysql_cnx)

        # ensure user is a teacher
        if not await role_in_classroom(user_id, class_id, mysql_repo) == 'teacher':
            raise HTTPException(status_code=403, detail='Forbidden. You are not a teacher in this classroom.')

        return await mysql_repo['classroom'].get_invitation_code(class_id)
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")


@CLASSROOM_CONTROLLER.put("/classroom/{class_id}/update", response_model=dict)
async def update_classroom_by_id(
        class_id: str,
        user_id: str=Depends(verify_token),
        class_name: str = Form(None),
        subject_name: str = Form(None),
        class_schedule: str = Form(None),
        description: str = Form(None),
        mysql_cnx=Depends(get_mysql_connection)
) -> dict:
    try:
        if not user_id:
            raise HTTPException(status_code=403, detail='Unauthorized. Try to login again before accessing this resource.')

        mysql_repo = await get_mysql_repo(mysql_cnx)

        # ensure user is classroom's owner
        if not await is_classroom_owner(user_id, class_id, mysql_repo):
            raise HTTPException(status_code=403, detail='Forbidden. You are not the owner of this classroom.')

        # update classroom
        information = {
            'class_name': class_name if class_name else None,
            'subject_name': subject_name if subject_name else None,
            'class_schedule': class_schedule if class_schedule else None,
            'description': description if description else None,
        }
        information = {k:v for k, v in information.items() if v is not None}
        update_info = ClassroomUpdate(**information)

        if not await mysql_repo['classroom'].update_by_id(class_id, update_info):
            raise HTTPException(status_code=500,
                                detail=f'Unexpected error occurred. Update classroom {class_id} failed')

        new_info = update_info.model_dump(exclude_unset=True)
        return {
            'message': f'Updated classroom {class_id} successfully',
            'class_id': class_id,
            'new_info': new_info,
        }
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")


@CLASSROOM_CONTROLLER.delete("/classroom/{class_id}/delete", response_model=dict)
async def delete_classroom_by_id(
        class_id: str,
        user_id: str=Depends(verify_token),
        mysql_cnx=Depends(get_mysql_connection),
        mongo_cnx=Depends(get_mongo_connection)
) -> dict:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        mysql_repo = await get_mysql_repo(mysql_cnx, auto_commit=False)
        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure that user is classroom's owner
        if not await is_classroom_owner(user_id, class_id, mysql_repo):
            raise HTTPException(status_code=403, detail='Forbidden. You are not the owner of this classroom.')

        # delete classroom
        status1 = await mysql_repo['classroom'].delete_by_id(class_id)
        status2 = await mongo_repo['classroom'].delete_by_id(class_id)
        await handle_transaction([status1, status2], mysql_cnx)

        return {
            'message': f'Deleted classroom successfully',
            'class_id': class_id,
        }
    except MySQLError as e:
        mysql_cnx.rollback()
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")
    except PyMongoError as e:
        mysql_cnx.rollback()
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@CLASSROOM_CONTROLLER.put('/classroom/{class_id}/participant/add-student/{username}', response_model=dict)
async def add_student(
        class_id: str,
        username: str,
        user_id: str=Depends(verify_token),
        mysql_cnx=Depends(get_mysql_connection),
        mongo_cnx=Depends(get_mongo_connection)
) -> dict:
    """
    For teacher to add student to classroom
    """
    try:
        if not user_id:
            raise HTTPException(status_code=403, detail='Unauthorized. Try to login again before accessing this resource.')

        mysql_repo = await get_mysql_repo(mysql_cnx, auto_commit=False)
        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure user is teacher
        if await role_in_classroom(user_id, class_id, mysql_repo) != 'teacher':
            raise HTTPException(status_code=403, detail='Forbidden. You are not a teacher in this classroom')

        # add participant
        db_user = await mysql_repo['user'].get_by_username(username)
        status1 = await mysql_repo['classroom'].add_participant(db_user['id'], class_id, role='student')
        status2 = await mongo_repo['classroom'].add_participant(db_user['id'], db_user['username'], class_id, role='student')
        await handle_transaction([status1, status2], mysql_cnx)

        return {
            'message': f'Added student successfully',
            'student_id': db_user['id'],
        }
    except MySQLError as e:
        mysql_cnx.rollback()
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")
    except PyMongoError as e:
        mysql_cnx.rollback()
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@CLASSROOM_CONTROLLER.put('/classroom/{class_id}/participant/add-teacher/{username}', response_model=dict)
async def add_teacher(
        class_id: str,
        username: str,
        user_id: str=Depends(verify_token),
        mysql_cnx=Depends(get_mysql_connection),
        mongo_cnx=Depends(get_mongo_connection)
) -> dict:
    """
    For owner to add teacher to classroom
    """
    try:
        if not user_id:
            raise HTTPException(status_code=403, detail='Unauthorized. Try to login again before accessing this resource.')

        mysql_repo = await get_mysql_repo(mysql_cnx, auto_commit=False)
        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure that user is classroom's owner
        if not await is_classroom_owner(user_id, class_id, mysql_repo):
            raise HTTPException(status_code=403, detail='Forbidden. You are not the owner of this classroom.')

        # add participant
        db_user = await mysql_repo['user'].get_by_username(username)
        status1 = await mysql_repo['classroom'].add_participant(db_user['id'], class_id, role='teacher')
        status2 = await mongo_repo['classroom'].add_participant(db_user['id'], db_user['username'], class_id, role='teacher')
        await handle_transaction([status1, status2], mysql_cnx)

        return {
            'message': 'Added teacher successfully',
            'teacher_id': db_user['id'],
        }
    except MySQLError as e:
        mysql_cnx.rollback()
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")
    except PyMongoError as e:
        mysql_cnx.rollback()
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@CLASSROOM_CONTROLLER.delete('/classroom/{class_id}/participant/remove-student/{username}', response_model=dict)
async def remove_student(
        class_id: str,
        username: str,
        user_id: str=Depends(verify_token),
        mysql_cnx=Depends(get_mysql_connection),
        mongo_cnx=Depends(get_mongo_connection)
) -> dict:
    """
    For teacher to remove a participant from classroom
    """
    try:
        if not user_id:
            raise HTTPException(status_code=403, detail='Unauthorized. Try to login again before accessing this resource.')

        mysql_repo = await get_mysql_repo(mysql_cnx, auto_commit=False)
        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure user is teacher
        if not role_in_classroom(user_id, class_id, mysql_repo) != 'teacher':
            raise HTTPException(status_code=403, detail='Forbidden. You are not a teacher')

        # remove participant
        db_user = await mysql_repo['user'].get_by_username(username)
        status1 = await mysql_repo['classroom'].remove_participant(db_user['id'], class_id, role='student')
        status2 = await mongo_repo['classroom'].remove_participant(db_user['id'], class_id, role='student')
        await handle_transaction([status1, status2], mysql_cnx)

        return {
            'message': f'Removed student successfully',
            'student_id': db_user['id'],
        }
    except MySQLError as e:
        mysql_cnx.rollback()
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")
    except PyMongoError as e:
        mysql_cnx.rollback()
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@CLASSROOM_CONTROLLER.delete('/classroom/{class_id}/participant/remove-teacher/{username}', response_model=dict)
async def remove_teacher(
        class_id: str,
        username: str,
        user_id: str=Depends(verify_token),
        mysql_cnx=Depends(get_mysql_connection),
        mongo_cnx=Depends(get_mongo_connection)
) -> dict:
    """
    For owner to remove a teacher from classroom
    """
    try:
        if not user_id:
            raise HTTPException(status_code=403, detail='Unauthorized. Try to login again before accessing this resource.')

        mysql_repo = await get_mysql_repo(mysql_cnx, auto_commit=False)
        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure that user is classroom's owner
        if not is_classroom_owner(user_id, class_id, mysql_repo):
            raise HTTPException(status_code=403, detail='Forbidden. You are not the owner of this classroom.')

        # remove participant
        db_user = await mysql_repo['user'].get_by_username(username)
        status1 = await mysql_repo['classroom'].remove_participant(db_user['id'], class_id, role='teacher')
        status2 = await mongo_repo['classroom'].remove_participant(db_user['id'], class_id, role='teacher')
        await handle_transaction([status1, status2], mysql_cnx)

        return {
            'message': f'Removed teacher successfully',
            'teacher_id': db_user['id'],
        }
    except MySQLError as e:
        mysql_cnx.rollback()
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")
    except PyMongoError as e:
        mysql_cnx.rollback()
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")
