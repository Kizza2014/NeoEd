from typing import Any
from config import MongoDBManager
from abc import abstractmethod

class MongoDBRepository:
    DB = 'mid_term'

    def __init__(self, mongodb: MongoDBManager):
        self.mongodb = mongodb
        self.database = self.mongodb.get_db(MongoDBRepository.DB)
        self.session = self.mongodb.get_session()

    @abstractmethod
    def get_all(self, session=None):
        pass

    @abstractmethod
    def get_by_id(self, item_id: Any, session=None):
        pass

    @abstractmethod
    def update_by_id(self, item_id: Any, update_info: dict, session=None):
        pass

    @abstractmethod
    def delete_by_id(self, item_id: Any, session=None):
        pass

    @abstractmethod
    def insert(self, item: dict, session=None):
        pass