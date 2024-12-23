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


    async def create_classroom(self, new_classroom: ClassroomCreate) -> bool:
        class_info = new_classroom.model_dump()
        class_info['_id'] = class_info['id']
        class_info.pop('id')

        class_info['posts'] = []
        class_info['assignments'] = []
        class_info['participants'] = []

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


    async def add_participant(self, username: str, class_id: str) -> bool:
        res = self.collection.find_one_and_update({'_id': class_id}, {'$addToSet': {'participants': username}})
        if res is None:
            raise PyMongoError("Classroom not found")
        return True

    async def remove_participant(self, username: str, class_id: str) -> bool:
        res = self.collection.find_one_and_update({'_id': class_id}, {'$pull': {'participants': username}})
        if res is None:
            raise PyMongoError("Classroom not found")
        return True