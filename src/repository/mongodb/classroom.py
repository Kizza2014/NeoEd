from pymongo.errors import PyMongoError
from src.repository.mongodb.mongodb_repository import MongoDBRepositoryInterface
from src.service.models.classroom import ClassroomCreate
from typing import List


class MongoClassroomRepository(MongoDBRepositoryInterface):
    def __init__(self, connection):
        super().__init__(connection)
        self.collection = self.connection.get_collection("classes")


    async def get_by_id(self, class_id: str) -> dict | None:
        return self.collection.find_one({'_id': class_id})


    async def create_classroom(self, new_classroom: ClassroomCreate, owner_username: str) -> bool:
        class_info = {
            '_id': new_classroom.id,
            'posts': [],
            'assignments': [],
            'participants': [{'user_id': new_classroom.owner_id, 'username': owner_username}]
        }

        res = self.collection.insert_one(class_info)
        return res.acknowledged


    async def delete_by_id(self, class_id: str) -> bool:
        res = self.collection.find_one_and_delete({'_id': class_id})
        if res is None:
            raise PyMongoError("Classroom not found")
        return True


    async def get_all_participants(self, class_id: str) -> List[str]:
        db_class = self.collection.find_one({'_id': class_id})
        if not db_class:
            raise PyMongoError("Classroom not found")
        return db_class['participants']


    async def add_participant(self, user_id: str, username: str, class_id: str) -> bool:
        filters = {'_id': class_id}
        updates = {
            '$addToSet': {
                'participants': {'user_id': user_id, 'username': username}
            }
        }
        res = self.collection.find_one_and_update(filters, updates)
        if res is None:
            raise PyMongoError("Classroom not found")
        return True


    async def remove_participant(self, user_id: str, class_id: str) -> bool:
        filters = {'_id': class_id}
        updates = {
            '$pull': {
                'participants': {'user_id': user_id}
            }
        }
        res = self.collection.find_one_and_update(filters, updates)
        if res is None:
            raise PyMongoError("Classroom not found")
        return True