from src.repository.mysql import ClassroomRepository
from fastapi import APIRouter, Depends
from src.configs.connections.mysql import get_mysql_conn
from typing import List
from src.service.models import Classroom


CLASSROOM_CONTROLLER = APIRouter()


# @CLASSROOM_CONTROLLER.get("/classrooms", response_model=List[Classroom])
# async def get_all(conn=Depends(get_mysql_conn)):
#     repo = ClassroomRepository(conn)
#     return repo.get_all()
#
#
# @CLASSROOM_CONTROLLER.get("/classrooms/{class_id}", response_model=Classroom)
# async def get_by_id(class_id: str, conn=Depends(get_mysql_conn)):
#     repo = ClassroomRepository(conn)
#     return repo.get_by_id(class_id)
#
#
# @CLASSROOM_CONTROLLER.put("/classrooms/{class_id}")
# async def update_by_id(class_id: str, new_item: Classroom, conn=Depends(get_mysql_conn)):
#     repo = ClassroomRepository(conn)
#     if not repo.update_by_id(class_id, new_item):
#         return False
#     return new_item
#
#
# @CLASSROOM_CONTROLLER.post("/classrooms")
# async def create(new_classroom: Classroom, conn=Depends(get_mysql_conn)):
#     repo = ClassroomRepository(conn)
#     if not repo.insert(new_classroom):
#         return False
#     return new_classroom
#
#
# @CLASSROOM_CONTROLLER.delete("/classrooms/{class_id}")
# async def delete_by_id(class_id: str, conn=Depends(get_mysql_conn)):
#     repo = ClassroomRepository(conn)
#     return repo.delete_by_id(class_id)