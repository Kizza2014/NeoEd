from pymongo.errors import DuplicateKeyError
from .mongodb_repository import MongoDBRepository
from config import MongoDBManager

class UserRepository(MongoDBRepository):
    COLLECTION = 'users'

    def __init__(self, mongodb: MongoDBManager):
        super().__init__(mongodb)
        self.collection = self.database.get_collection(self.COLLECTION)

    def get_all(self, session=None):
        users = self.collection.find(session=session)
        return users.to_list()

    def get_by_id(self, user_id: int, session=None):
        user = self.collection.find_one({'_id': user_id}, session=session)
        return user

    def update_by_id(self, user_id: int, update_info: dict, session=None):
        updated_user = self.collection.find_one_and_update({'_id': user_id}, {'$set': update_info}, session=session)
        return updated_user

    def delete_by_id(self, user_id: int, session=None):
        deleted_user = self.collection.find_one_and_delete({'_id': user_id}, session=session)
        return deleted_user

    def insert(self, item: dict, session=None):
        try:
            new_user = self.collection.insert_one(item, session=session)
            return new_user
        except DuplicateKeyError:
            print('_id duplicated')

    def get_cart(self, user_id, session=None):
        user = self.get_by_id(user_id, session=session)
        if user.get('cart', None) is None:
            self.collection.find_one_and_update({'_id': user_id}, {'$set': {'cart': []}}, session=session)
        return user.get('cart', [])

    def add_to_cart(self, user_id, item: dict, session=None):
        item_id = item['_id']
        qty = item['quantity']
        update_result = self.collection.update_one(
            {
                '_id': user_id,
                'cart._id': item_id},
                {'$inc': {'cart.$.quantity': qty}
            },
            session=session
        )
        if update_result.modified_count == 0:
            self.collection.update_one({'_id': user_id}, {'$push': {'cart': item}}, session=session)

        return item

    def clear_cart(self, user_id: int, session=None):
        self.collection.find_one_and_update({'_id': user_id}, {'$set': {'cart': []}}, session=session)

    def update_cart(self):
        pass

    def add_transaction(self, user_id: int, trans: dict, session=None):
        self.collection.find_one_and_update(
            {'_id': user_id},
            {'$push': {'transaction_history': trans}},
            session=session
        )

    def reduce_balance(self, user_id: int, amount: float, session=None):
        self.collection.find_one_and_update({'_id': user_id}, {'$inc': {'balance': -amount}}, session=session)

    def add_bought_books(self, user_id: int, item: dict, session=None):
        bought_book = {
            '_id': item['_id'],
            'title': item['title']
        }
        self.collection.find_one_and_update(
            {'_id': user_id},
            {'$addToSet': {'bought_books': bought_book}},
            session=session
        )