from src.repository.mysql import MySQLClassroomRepository
from src.repository.mongodb import MongoClassroomRepository
from fastapi import APIRouter, Depends
from src.configs.connections.mysql import get_mysql_connection
from src.configs.connections.mongodb import get_mongo_connection
from src.service.models import (
    ClassroomCreate, ClassroomResponse,
    ClassroomUpdate
)
from mysql.connector import Error as MySQLError
from pymongo.errors import PyMongoError
from fastapi import HTTPException
from datetime import datetime
from typing import List


CLASSROOM_CONTROLLER = APIRouter()


# TEST API

@CLASSROOM_CONTROLLER.get("/classroom/all", response_model=List[ClassroomResponse])
async def get_all(connection=Depends(get_mysql_connection)):
    try:
        repo = MySQLClassroomRepository(connection)
        query_result = await repo.get_all()
        return [ClassroomResponse(**classroom) for classroom in query_result]
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")


@CLASSROOM_CONTROLLER.get("/classroom/{class_id}/detail", response_model=ClassroomResponse)
async def get_by_id(class_id: str, connection=Depends(get_mysql_connection)):
    try:
        repo = MySQLClassroomRepository(connection)
        db_classroom = await repo.get_by_id(class_id)
        if not db_classroom:
            raise HTTPException(status_code=404, detail="Classroom not found")
        return db_classroom
    except MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@CLASSROOM_CONTROLLER.post("/classroom/create")
async def create_classroom(
        new_classroom: ClassroomCreate,
        mysql_connection=Depends(get_mysql_connection),
        mongo_connection=Depends(get_mongo_connection)
):
    try:
        mysql_repo = MySQLClassroomRepository(mysql_connection, auto_commit=False)
        mongo_repo = MongoClassroomRepository(mongo_connection)

        current_time = datetime.now()
        formated_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
        new_classroom.id = '_'.join([new_classroom.owner, formated_time])

        status1 = await mysql_repo.create_classroom(new_classroom)
        status2 = await mysql_repo.add_participant(new_classroom.owner, new_classroom.id)
        status3 = await mongo_repo.create_classroom(new_classroom)
        status4 = await mongo_repo.add_participant(new_classroom.owner, new_classroom.id)
        if not all([status1, status2, status3, status4]):
            mysql_connection.rollback()
            raise HTTPException(status_code=500, detail='An unexpected error occurred. Create classroom failed')
        mysql_connection.commit()

        return {
            'message': f'Created classroom {new_classroom.class_name} successfully',
            'class_id': new_classroom.id,
        }
    except MySQLError as e:
        mysql_connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@CLASSROOM_CONTROLLER.put("/classroom/{class_id}/update")
async def update_by_id(class_id: str, update_info: ClassroomUpdate, connection=Depends(get_mysql_connection)):
    try:
        repo = MySQLClassroomRepository(connection)
        if not await repo.update_by_id(class_id, update_info):
            raise HTTPException(status_code=500, detail=f'Unexpected error occurred. Update classroom {class_id} failed')

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
async def delete_by_id(
        class_id: str,
        mysql_connection=Depends(get_mysql_connection),
        mongo_connection=Depends(get_mongo_connection)
):
    try:
        mysql_repo = MySQLClassroomRepository(mysql_connection, auto_commit=False)
        mongo_repo = MongoClassroomRepository(mongo_connection)

        status1 = await mysql_repo.delete_by_id(class_id)
        status2 =await mongo_repo.delete_by_id(class_id)
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
@CLASSROOM_CONTROLLER.get('/classroom/{class_id}/participant/all', response_model=List[str])
async def get_all_participants(class_id: str, connection=Depends(get_mongo_connection)):
    try:
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
    try:
        mysql_repo = MySQLClassroomRepository(mysql_connection, auto_commit=False)
        mongo_repo = MongoClassroomRepository(mongo_connection)

        status1 = await mysql_repo.add_participant(username, class_id)
        status2 = await mongo_repo.add_participant(username, class_id)
        if not all([status1, status2]):
            mysql_connection.rollback()
            raise HTTPException(status_code=500, detail='An unexpected error occurred. Please try again later')

        mysql_connection.commit()
        return {
            'message': f'Added participant {username} successfully',
            'username': username,
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
    try:
        mysql_repo = MySQLClassroomRepository(mysql_connection, auto_commit=False)
        mongo_repo = MongoClassroomRepository(mongo_connection)

        status1 = await mysql_repo.remove_participant(username, class_id)
        status2 = await mongo_repo.remove_participant(username, class_id)

        if not all([status1, status2]):
            mysql_connection.rollback()
            raise HTTPException(status_code=500, detail='An unexpected error occurred. Please try again later')

        mysql_connection.commit()
        return {
            'message': f'Removed participant {username} successfully',
            'username': username,
        }
    except MySQLError as e:
        mysql_connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database MySQL error: {str(e)}")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")
