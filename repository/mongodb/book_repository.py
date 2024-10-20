from .mongodb_repository import MongoDBRepository
from pymongo.errors import DuplicateKeyError
from config import MongoDBManager
from typing import List


class BookRepository(MongoDBRepository):
    COLLECTION = 'books'

    def __init__(self, mongodb: MongoDBManager):
        super().__init__(mongodb)
        self.collection = self.database.get_collection(BookRepository.COLLECTION)

    def get_all(self, session=None):
        books = self.collection.find(session=session)
        return books.to_list()


    def get_by_id(self, item_id, session=None):
        book = self.collection.find_one({'_id':item_id}, session=session)
        return book

    def get_many_by_id(self, item_ids: List[str], session=None):
        books = []
        for item_id in item_ids:
            book = self.collection.find_one({'_id': item_id}, session=session)
            books.append(book)
        return books

    def update_by_id(self, item_id: str, update_info: dict, session=None):
        updated_book = self.collection.find_one_and_update({'_id': item_id}, {'$set': update_info}, session=session)
        return updated_book

    def delete_by_id(self, item_id: str, session=None):
        deleted_book = self.collection.find_one_and_delete({'_id': item_id}, session=session)
        return deleted_book

    def insert(self, item: dict, session=None):
        try:
            new_book = self.collection.insert_one(item, session=session)
            return new_book
        except DuplicateKeyError:
            print('_id duplicated.')


    def get_by_keyword(self, keywords: str, session=None):
        keywords = keywords.split(',')
        search_value = ["\"" + keyword.strip() + "\"" for keyword in keywords]
        search_value = ' '.join(search_value)
        books = self.collection.find({'$text': {'$search': search_value}}, session=session)
        return books.to_list()

    def reduce_quantity(self, item_id: str, amount: int, session=None):
        self.collection.find_one_and_update({'_id': item_id}, {'$inc': {'available_copies': -amount}}, session=session)
