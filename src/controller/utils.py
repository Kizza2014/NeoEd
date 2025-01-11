from src.repository.mysql.classroom import MySQLClassroomRepository
from src.repository.mysql.user import UserRepository
from src.repository.mongodb.classroom import MongoClassroomRepository
from src.repository.mongodb.assignment import AssignmentRepository
from src.repository.mongodb.post import PostRepository
from typing import TypedDict
from fastapi import HTTPException


class MySQLRepo(TypedDict):
    classroom: MySQLClassroomRepository
    user: UserRepository

class MongoRepo(TypedDict):
    classroom: MongoClassroomRepository
    assignment: AssignmentRepository
    post: PostRepository

async def get_mysql_repo(mysql_cnx=None, auto_commit=True) -> MySQLRepo:
    repo = {}
    if mysql_cnx:
        repo['classroom'] = MySQLClassroomRepository(mysql_cnx, auto_commit)
        repo['user'] = UserRepository(mysql_cnx, auto_commit)
    return repo

async def get_mongo_repo(mongo_cnx=None) -> MongoRepo:
    repo = {}
    if mongo_cnx:
        repo['classroom'] = MongoClassroomRepository(mongo_cnx)
        repo['assignment'] = AssignmentRepository(mongo_cnx)
        repo['post'] = PostRepository(mongo_cnx)
    return repo

async def handle_transaction(statuses, mysql_cnx):
    if not all(statuses):
        mysql_cnx.rollback()
        raise HTTPException(status_code=500, detail='An unexpected error occurred. Please try again later')
    mysql_cnx.commit()

async def role_in_classroom(user_id: str, class_id: str, mysql_repo: MySQLRepo) -> str:
    return await mysql_repo['classroom'].get_user_role(user_id, class_id)
