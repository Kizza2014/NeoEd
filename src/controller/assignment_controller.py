from src.repository.mysql import AssignmentRepository
from fastapi import APIRouter, Depends
from src.configs.connections.mysql import get_mysql_conn
from typing import List
from src.service.models import Assignment


ASSIGNMENT_CONTROLLER = APIRouter()


# @ASSIGNMENT_CONTROLLER.get("/assignments", response_model=List[Assignment])
# async def get_all(conn=Depends(get_mysql_conn)):
#     repo = AssignmentRepository(conn)
#     return repo.get_all()
#
#
# @ASSIGNMENT_CONTROLLER.get("/assignments/{assignment_id}", response_model=Assignment)
# async def get_by_id(assignment_id: str, conn=Depends(get_mysql_conn)):
#     repo = AssignmentRepository(conn)
#     return repo.get_by_id(assignment_id)
#
#
# @ASSIGNMENT_CONTROLLER.put("/assignments/{assignment_id}")
# async def update_by_id(assignment_id: str, new_item: Assignment, conn=Depends(get_mysql_conn)):
#     repo = AssignmentRepository(conn)
#     if not repo.update_by_id(assignment_id, new_item):
#         return False
#     return new_item
#
#
# @ASSIGNMENT_CONTROLLER.post("/assignments")
# async def create(new_assignment: Assignment, conn=Depends(get_mysql_conn)):
#     repo = AssignmentRepository(conn)
#     if not repo.insert(new_assignment):
#         return False
#     return new_assignment
#
#
# @ASSIGNMENT_CONTROLLER.delete("/assignments/{assignment_id}")
# async def delete_by_id(assignment_id: str, conn=Depends(get_mysql_conn)):
#     repo = AssignmentRepository(conn)
#     return repo.delete_by_id(assignment_id)