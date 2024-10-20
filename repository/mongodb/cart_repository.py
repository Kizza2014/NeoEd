from typing import Any

from .mongodb_repository import MongoDBRepository
from config import MongoDBManager


class CartRepository(MongoDBRepository):
    COLLECTION = 'carts'

    def __init__(self, mongodb: MongoDBManager):
        super().__init__(mongodb)
        self.collection = self.database.get_collection(CartRepository.COLLECTION)

    def get_by_id(self, item_id):
        cart = self.collection.find_one({'_id':item_id})
        return cart

    def insert_item(self, cart_id: int, item: dict):
        inserted_item = self.collection.find_one_and_update({'_id': cart_id}, {'$push': {'items': item}})
        return inserted_item

    def delete_item(self, cart_id: int, item_id: str):
        deleted_item = self.collection.find_one_and_update({'_id': cart_id}, {'$pull': {'items': {'_id': item_id}}})
        return deleted_item

    def clear_cart(self, cart_id: int):
        cart = self.collection.find_one_and_replace({'_id': cart_id}, self._empty_cart(cart_id))
        return cart

    def _empty_cart(self, cart_id):
        return {
            '_id': cart_id,
            'items': []
        }

    def update_by_id(self, item_id: Any, update_info: dict):
        pass

    def delete_by_id(self, item_id: Any):
        pass

    def insert(self, item: dict):
        pass

    def get_all(self):
        pass