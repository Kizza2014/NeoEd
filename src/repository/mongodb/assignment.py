from src.repository.mongodb import MongoDBRepositoryInterface
from src.service.models.classroom import AssignmentUpdate, AssignmentCreate
from typing import List
from datetime import datetime


class AssignmentRepository(MongoDBRepositoryInterface):
    def __init__(self, connection):
        super().__init__(connection)
        self.collection = self.connection.get_collection("classes")


    async def get_all(self, class_id: str) -> List[dict]:
        db_classroom = self.collection.find_one({'_id': class_id})
        return db_classroom['assignments']


    async def get_by_id(self, class_id: str, assgn_id: str) -> dict | None:
        db_classroom = self.collection.find_one({'_id': class_id})
        if db_classroom is not None:
            for assignment in db_classroom['assignments']:
                if assignment['id'] == assgn_id:
                    return assignment
        return None


    async def create_assignment(self, class_id: str, new_assgn: AssignmentCreate) -> bool:
        assgn_info = new_assgn.model_dump()
        created_at = datetime.now()
        assgn_info['id'] = '_'.join([new_assgn.author, created_at.strftime('%Y_%m_%d_%H_%M_%S')])
        assgn_info['created_at'] = created_at
        assgn_info['updated_at'] = created_at

        filters = {'_id': class_id}
        updates = {
            '$push': {
                'assignments': assgn_info
            }
        }

        res = self.collection.update_one(filters, updates)
        if res.modified_count > 0:
            return assgn_info['id']
        return None


    async def update_by_id(self, class_id: str, assgn_id: str, new_info: AssignmentUpdate) -> bool:
        current_time = datetime.now()

        update_info = new_info.model_dump(exclude_unset=True)
        filters = {'_id': class_id, 'assignments.id': assgn_id}
        updates = {
            '$set': {}
        }
        set_op = updates['$set']
        for key, value in update_info.items():
            set_op['assignments.$.' + key] = value
        set_op['assignments.$.updated_at'] = current_time

        result = self.collection.update_one(filters, updates)
        return result.modified_count > 0


    async def delete_by_id(self, class_id: str, assgn_id: str) -> bool:
        filters = {'_id': class_id}
        updates = {
            '$pull': {
                'assignments': {'id': assgn_id}
            }
        }
        result = self.collection.update_one(filters, updates)
        return result.modified_count > 0
