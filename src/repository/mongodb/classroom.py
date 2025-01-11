from pymongo.errors import PyMongoError
from src.repository.mongodb.mongodb_repository import MongoDBRepositoryInterface
from src.service.models.classroom import ClassroomCreate
from pytz import timezone
from datetime import datetime


class MongoClassroomRepository(MongoDBRepositoryInterface):
    def __init__(self, connection):
        super().__init__(connection)
        self.collection = self.connection.get_collection("classes")

    async def get_by_id(self, class_id: str) -> dict | None:
        return self.collection.find_one({'_id': class_id})

    async def create_classroom(self, new_classroom: ClassroomCreate) -> bool:
        class_info = {
            '_id': new_classroom.id,
            'posts': [],
            'assignments': [],
            'participants': [{'user_id': new_classroom.owner_id, 'username': new_classroom.owner_username, 'role': 'teacher'}]
        }

        res = self.collection.insert_one(class_info)
        return res.acknowledged

    async def create_classroom_from_template(self, template, new_id: str) -> bool:
        current_time = datetime.now(timezone('Asia/Ho_Chi_Minh'))
        db_classroom = self.collection.find_one({'_id': template['id']})
        if db_classroom is None:
            raise PyMongoError("Template not found")

        db_classroom['_id'] = new_id
        teachers_username = [participant['username'] for participant in db_classroom['participants'] if participant['role'] == 'teacher']
        db_classroom['participants'] = [{'user_id': template['owner_id'], 'username': template['owner_username'], 'role': 'teacher'}]

        # only keep posts from teachers
        posts = []
        for post in db_classroom['posts']:
            if post['author'] in teachers_username:
                post['author'] = template['owner_username']
                post['created_at'] = current_time
                post['updated_at'] = current_time
                posts.append(post)
        db_classroom['posts'] = posts
        # empty assignments submissions
        for assignment in db_classroom['assignments']:
            assignment['author'] = template['owner_username']
            assignment['submissions'] = []
            assignment['created_at'] = current_time
            assignment['updated_at'] = current_time

        res = self.collection.insert_one(db_classroom)
        return res.acknowledged

    async def delete_by_id(self, class_id: str) -> bool:
        res = self.collection.find_one_and_delete({'_id': class_id})
        if res is None:
            raise PyMongoError("Classroom not found")
        return True

    async def get_all_participants(self, class_id: str) -> dict:
        db_class = self.collection.find_one({'_id': class_id})
        if not db_class:
            raise PyMongoError("Classroom not found")
        participants = db_class.get('participants', [])
        return {
            'teachers': [participant for participant in participants if participant['role'] == 'teacher'],
            'students': [participant for participant in participants if participant['role'] == 'student']
        }

    async def add_participant(self, user_id: str, username: str, class_id: str, role: str) -> bool:
        filters = {'_id': class_id}
        updates = {
            '$addToSet': {
                'participants': {'user_id': user_id, 'username': username, 'role': role}
            }
        }
        res = self.collection.find_one_and_update(filters, updates)
        return res is not None

    async def find_participant_in_class(self, user_id: str, class_id: str) -> bool:
        db_class = self.collection.find_one({'_id': class_id})
        if not db_class:
            raise PyMongoError("Classroom not found")
        return any(participant['user_id'] == user_id for participant in db_class['participants'])

    async def remove_participant(self, user_id: str, class_id: str, role: str) -> bool:
        filters = {'_id': class_id}
        updates = {
            '$pull': {
                'participants': {'user_id': user_id, 'role': role}
            }
        }
        res = self.collection.find_one_and_update(filters, updates)
        return res is not None