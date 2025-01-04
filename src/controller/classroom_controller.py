from src.repository.mysql.classroom import MySQLClassroomRepository
from src.repository.mongodb.classroom import MongoClassroomRepository
from fastapi import APIRouter, Depends
from src.configs.connections.mysql import get_mysql_connection
from src.configs.connections.mongodb import get_mongo_connection
from src.service.models.classroom import (
    ClassroomCreate, ClassroomResponse,
    ClassroomUpdate
)
from mysql.connector import Error as MySQLError
from pymongo.errors import PyMongoError
from fastapi import HTTPException, UploadFile, File, Form
from typing import List
import uuid

CLASSROOM_CONTROLLER = APIRouter(tags=['Classroom'])

# TODO: replace with user from token
current_user = {
    'id': 'user-ffe17039-f1e6-41dd-87f4-659489c4cd0d',
    'username': 'robinblake',
    'fullname': 'robinblake',
    'gender': 'Other',
    'role': 'Teacher'
}


@CLASSROOM_CONTROLLER.get("/classroom/all", response_model=List[ClassroomResponse])
async def get_my_classrooms(connection=Depends(get_mysql_connection)):
    try:
        # TODO: replace with user from token
        # Ensure user is logged in
        if not current_user:
            raise HTTPException(status_code=403, detail='Unauthorized. You must login before accessing this resource.')

        repo = MySQLClassroomRepository(connection)
        query_result = await repo.get_all_classroom_of_user(current_user['id'])

        return [ClassroomResponse(**classroom) for classroom in query_result]
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")


@CLASSROOM_CONTROLLER.get("/classroom/{class_id}/detail", response_model=ClassroomResponse)
async def get_classroom_by_id(class_id: str, connection=Depends(get_mysql_connection)):
    try:
        # TODO: replace with user from token
        # ensure user is logged in
        if not current_user:
            raise HTTPException(status_code=403, detail='Unauthorized. You must login before accessing this resource.')

        repo = MySQLClassroomRepository(connection)
        db_classroom = await repo.get_by_id(class_id)
        if not db_classroom:
            raise HTTPException(status_code=404, detail="Classroom not found")

        return db_classroom
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@CLASSROOM_CONTROLLER.post("/classroom/create")
async def create_classroom(
        class_name: str = Form(...),
        subject_name: str = Form(...),
        class_schedule: str = Form(None),
        description: str = Form(None),
        password: str = Form(...),
        require_password: bool = Form(False),
        mysql_connection=Depends(get_mysql_connection),
        mongo_connection=Depends(get_mongo_connection)
):
    try:
        # TODO: replace with user from token
        # ensure user is logged in
        if not current_user:
            raise HTTPException(status_code=403, detail='Unauthorized. You must login before accessing this resource.')

        # ensure user is a teacher
        if current_user.get('role', None) != 'Teacher':
            raise HTTPException(status_code=403, detail='Only teacher can create classroom.')

        # create classroom
        information = {
            'class_name': class_name,
            'subject_name': subject_name,
            'class_schedule': class_schedule if class_schedule else None,
            'description': description if description else None,
            'owner_id': current_user['id'],
            'password': password,
            'require_password': require_password
        }
        information = {k: v for k, v in information.items() if v is not None}
        class_id = 'classroom-' + str(uuid.uuid4())
        new_classroom = ClassroomCreate(**information, id=class_id)

        mysql_repo = MySQLClassroomRepository(mysql_connection, auto_commit=False)
        mongo_repo = MongoClassroomRepository(mongo_connection)

        # transaction-like operation
        status1 = await mysql_repo.create_classroom(new_classroom)
        status2 = await mysql_repo.add_participant(new_classroom.owner_id, class_id)
        status3 = await mongo_repo.create_classroom(new_classroom, current_user['username'])
        if not all([status1, status2, status3]):
            mysql_connection.rollback()
            raise HTTPException(status_code=500, detail='An unexpected error occurred. Create classroom failed')
        mysql_connection.commit()

        return {
            'message': f'Created classroom successfully',
            'class_id': class_id,
        }
    except MySQLError as e:
        mysql_connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@CLASSROOM_CONTROLLER.put("/classroom/{class_id}/update")
async def update_classroom_by_id(
        class_id: str,
        class_name: str = Form(None),
        subject_name: str = Form(None),
        class_schedule: str = Form(None),
        description: str = Form(None),
        password: str = Form(None),
        require_password: bool = Form(None),
        connection=Depends(get_mysql_connection)
):
    try:
        # ensure user is logged in
        if not current_user:
            raise HTTPException(status_code=403, detail='Unauthorized. You must login before accessing this resource.')

        mysql_repo = MySQLClassroomRepository(connection)

        # ensure user is classroom's owner
        class_owner_id = await mysql_repo.get_owner_id(class_id)
        if current_user['id'] != class_owner_id:
            raise HTTPException(status_code=403, detail='Forbidden. You are not the owner of this classroom.')

        # update classroom
        information = {
            'class_name': class_name if class_name else None,
            'subject_name': subject_name if subject_name else None,
            'class_schedule': class_schedule if class_schedule else None,
            'description': description if description else None,
            'password': password if password else None,
            'require_password': require_password if require_password is not None else None
        }
        information = {k: v for k, v in information.items() if v is not None}
        update_info = ClassroomUpdate(**information)

        if not await mysql_repo.update_by_id(class_id, update_info):
            raise HTTPException(status_code=500,
                                detail=f'Unexpected error occurred. Update classroom {class_id} failed')

        new_info = update_info.model_dump(exclude_unset=True)
        return {
            'message': f'Updated classroom {class_id} successfully',
            'class_id': class_id,
            'new_info': new_info,
        }
    except MySQLError as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")


@CLASSROOM_CONTROLLER.delete("/classroom/{class_id}/delete")
async def delete_classroom_by_id(
        class_id: str,
        mysql_connection=Depends(get_mysql_connection),
        mongo_connection=Depends(get_mongo_connection)
):
    try:
        # TODO: replace with user from token
        # ensure that user is logged in
        if not current_user:
            raise HTTPException(status_code=403, detail='Unauthorized. You must login before accessing this resource.')

        mysql_repo = MySQLClassroomRepository(mysql_connection, auto_commit=False)

        # ensure that user is classroom's owner
        class_owner_id = await mysql_repo.get_owner_id(class_id)
        if current_user['id'] != class_owner_id:
            raise HTTPException(status_code=403, detail='Forbidden. You are not the owner of this classroom.')

        # delete classroom
        mongo_repo = MongoClassroomRepository(mongo_connection)

        status1 = await mysql_repo.delete_by_id(class_id)
        status2 = await mongo_repo.delete_by_id(class_id)

        # transaction-like operation
        if not all([status1, status2]):
            mysql_connection.rollback()
            raise HTTPException(status_code=500, detail='An unexpected error occurred. Delete classroom failed')
        mysql_connection.commit()

        return {
            'message': f'Deleted classroom {class_id} successfully',
            'class_id': class_id,
        }
    except MySQLError as e:
        mysql_connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


# Classroom participants
@CLASSROOM_CONTROLLER.get('/classroom/{class_id}/participant/all', response_model=List[dict])
async def get_all_participants(class_id: str, connection=Depends(get_mongo_connection)):
    try:
        # TODO: replace with user from token
        # ensure that user is logged in
        if not current_user:
            raise HTTPException(status_code=403, detail='Unauthorized. You must login before accessing this resource.')

        mongo_repo = MongoClassroomRepository(connection)
        return await mongo_repo.get_all_participants(class_id)
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@CLASSROOM_CONTROLLER.put('/classroom/{class_id}/participant/add/{username}')
async def add_participant(
        class_id: str,
        username: str,
        mysql_connection=Depends(get_mysql_connection),
        mongo_connection=Depends(get_mongo_connection)
):
    """
    For teacher to add participant to classroom
    """
    try:
        # TODO: replace with user from token
        # ensure that user is logged in
        if not current_user:
            raise HTTPException(status_code=403, detail='Unauthorized. You must login before accessing this resource.')

        # ensure that user is classroom's owner
        mysql_repo = MySQLClassroomRepository(mysql_connection, auto_commit=False)
        class_owner_id = await mysql_repo.get_owner_id(class_id)
        if current_user['id'] != class_owner_id:
            raise HTTPException(status_code=403, detail='Forbidden. You are not the owner of this classroom.')

        # add participant
        mongo_repo = MongoClassroomRepository(mongo_connection)

        status1 = await mysql_repo.add_participant(current_user['id'], class_id)
        status2 = await mongo_repo.add_participant(current_user['id'], current_user['username'], class_id)

        # transaction-like operation
        if not all([status1, status2]):
            mysql_connection.rollback()
            raise HTTPException(status_code=500, detail='An unexpected error occurred. Please try again later')
        mysql_connection.commit()

        return {
            'message': f'Added participant successfully',
            'username': username,
        }
    except MySQLError as e:
        mysql_connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@CLASSROOM_CONTROLLER.put('/classroom/{class_id}/participant/join')
async def join_classroom(
        class_id: str,
        password: str = Form(None),
        mysql_connection=Depends(get_mysql_connection),
        mongo_connection=Depends(get_mongo_connection)
):
    """
    For student to join into classroom
    """
    try:
        # TODO: replace with user from token
        # ensure that user is logged in
        if not current_user:
            raise HTTPException(status_code=403, detail='Unauthorized. You must login before accessing this resource.')

        # verify classroom's password
        mysql_repo = MySQLClassroomRepository(mysql_connection, auto_commit=False)
        if not await mysql_repo.verify_password(class_id, password):
            raise HTTPException(status_code=403, detail='Forbidden. Incorrect password')

        # add participant
        mongo_repo = MongoClassroomRepository(mongo_connection)
        status2 = await mongo_repo.add_participant(current_user['id'], current_user['username'], class_id)
        status1 = await mysql_repo.add_participant(current_user['id'], class_id)
        mysql_connection.commit()

        # transaction-like operation
        if not all([status1, status2]):
            mysql_connection.rollback()
            raise HTTPException(status_code=500, detail='An unexpected error occurred. Please try again later')

        return {
            'message': 'Joined classroom successfully',
            'class_id': class_id,
        }
    except MySQLError as e:
        mysql_connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@CLASSROOM_CONTROLLER.delete('/classroom/{class_id}/participant/delete/{username}')
async def remove_participant(
        class_id: str,
        username: str,
        mysql_connection=Depends(get_mysql_connection),
        mongo_connection=Depends(get_mongo_connection)
):
    """
    For teacher to remove a participant from classroom
    """
    try:
        # TODO: replace with user from token
        # ensure that user is logged in
        if not current_user:
            raise HTTPException(status_code=403, detail='Unauthorized. You must login before accessing this resource.')

        # ensure that user is classroom's owner
        mysql_repo = MySQLClassroomRepository(mysql_connection, auto_commit=False)
        class_owner_id = await mysql_repo.get_owner_id(class_id)
        if current_user['id'] != class_owner_id:
            raise HTTPException(status_code=403, detail='Forbidden. You are not the owner of this classroom.')

        # remove participant
        mongo_repo = MongoClassroomRepository(mongo_connection)
        status1 = await mysql_repo.remove_participant(username, class_id)
        status2 = await mongo_repo.remove_participant(username, class_id)

        # transaction-like operation
        if not all([status1, status2]):
            mysql_connection.rollback()
            raise HTTPException(status_code=500, detail='An unexpected error occurred. Please try again later')
        mysql_connection.commit()

        return {
            'message': f'Removed participant successfully',
            'username': username,
        }
    except MySQLError as e:
        mysql_connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@CLASSROOM_CONTROLLER.delete('/classroom/{class_id}/participant/leave')
async def leave_classroom(
        class_id: str,
        mysql_connection=Depends(get_mysql_connection),
        mongo_connection=Depends(get_mongo_connection)
):
    """
    For student to leave a classroom
    """
    try:
        pass
    except Exception as e:
        pass
