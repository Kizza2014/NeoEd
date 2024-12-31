from src.repository.mongodb.assignment import AssignmentRepository
from fastapi import APIRouter, Depends, HTTPException
from src.configs.connections.mongodb import get_mongo_connection
from pymongo.errors import PyMongoError
from typing import List
from src.service.models.classroom.assignment import Assignment, AssignmentCreate, AssignmentUpdate


ASSIGNMENT_CONTROLLER = APIRouter()


@ASSIGNMENT_CONTROLLER.get("/classroom/{class_id}/assignment/all", response_model=List[Assignment])
async def get_all(class_id: str, connection=Depends(get_mongo_connection)):
    try:
        repo = AssignmentRepository(connection)
        query_result = await repo.get_all(class_id)
        return [Assignment(**assgn_dict) for assgn_dict in query_result]
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@ASSIGNMENT_CONTROLLER.get("/classroom/{class_id}/assignment/{assgn_id}/detail", response_model=Assignment)
async def get_by_id(class_id: str, assgn_id: str, connection=Depends(get_mongo_connection)):
    try:
        repo = AssignmentRepository(connection)
        query_result = await repo.get_by_id(class_id, assgn_id)
        if not query_result:
            raise HTTPException(status_code=404, detail="Assignment not found")
        return Assignment(**query_result)
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@ASSIGNMENT_CONTROLLER.post("/classroom/{class_id}/assignment/create")
async def create_assignment(
        class_id: str,
        new_assignment: AssignmentCreate,
        connection=Depends(get_mongo_connection)
):
    try:
        repo = AssignmentRepository(connection)
        status = await repo.create_assignment(class_id, new_assignment)
        if not status:
            raise HTTPException(status_code=500, detail="Unexpected error occurred. Failed to create assignment.")
        return {
            'message': 'Assignment created successfully',
            'assignment_title': new_assignment.title
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@ASSIGNMENT_CONTROLLER.put("/classroom/{class_id}/assignment/{assgn_id}/update")
async def update_by_id(
        class_id: str,
        assgn_id: str,
        update_info: AssignmentUpdate,
        connection=Depends(get_mongo_connection)
):
    try:
        repo = AssignmentRepository(connection)
        status = await repo.update_by_id(class_id, assgn_id, update_info)
        if not status:
            raise HTTPException(status_code=500, detail="Unexpected error occurred. Failed to update assignment.")
        return {
            'message': 'Assignment updated successfully',
            'assignment_id': assgn_id
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@ASSIGNMENT_CONTROLLER.delete("/classroom/{class_id}/assignment/{assignment_id}/delete")
async def delete_by_id(class_id: str, assgn_id: str, connection=Depends(get_mongo_connection)):
    try:
        repo = AssignmentRepository(connection)
        status = await repo.delete_by_id(class_id, assgn_id)
        if not status:
            raise HTTPException(status_code=500, detail="Unexpected error occurred. Failed to delete assignment.")
        return {
            'message': f'Deleted assignment successfully',
            'assignment_id': assgn_id,
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")