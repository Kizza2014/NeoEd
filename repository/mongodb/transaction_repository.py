from .mongodb_repository import MongoDBRepository
from config import MongoDBManager
from bson import ObjectId


class TransactionRepository(MongoDBRepository):
    COLLECTION = 'transactions'

    def __init__(self, mongodb: MongoDBManager):
        super().__init__(mongodb)
        self.collection = self.database.get_collection(TransactionRepository.COLLECTION)

    def get_all(self, session=None):
        trans = self.collection.find(session=session)
        return trans.to_list()


    def get_by_id(self, item_id, session=None):
        tran = self.collection.find_one({'_id':item_id}, session=session)
        return tran

    def update_by_id(self, item_id: str, update_info: dict, session=None):
        pass

    def delete_by_id(self, item_id: str, session=None):
        pass

    def insert(self, item: dict, session=None):
        self.collection.insert_one(item, session=session)

    def update_status(self, item_id: ObjectId, status: str, session=None):
        self.collection.find_one_and_update({'_id': item_id}, {'$set': {'status': status}}, session=session)