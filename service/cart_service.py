from config import MongoDBManager
from errors import InsufficientStockError
from repository import UserRepository, BookRepository

COVERS = ['hard_cover', 'soft_cover']

class CartService:
    def __init__(self, mongodb: MongoDBManager, user_repository: UserRepository, book_repository: BookRepository):
        self.mongodb = mongodb
        self.user_repository = user_repository
        self.book_repository = book_repository

    def get_cart(self, user_id: int):
        cart = self.user_repository.get_cart(user_id)
        total_amount = 0
        if len(cart) > 0:
            for item in cart:
                item_id = item["_id"]
                item_cover = item["cover"]
                item_in_db = self.book_repository.get_by_id(item_id)
                item_price = item_in_db["price"][item_cover]
                item["price"] = item_price
                total_amount += item_price * item["quantity"]

        return {
            'items': cart,
            'total_amount': total_amount
        }

    def add_to_cart(self, item: dict):
        user_id = item['user_id']
        item_id = item['item_id']
        title = item['title']
        cover = item['cover']
        qty = item['quantity']
        added_item = None

        session = self.mongodb.get_session()
        session.start_transaction()
        try:
            book = self.book_repository.get_by_id(item_id, session=session)
            available_copies = book.get('available_copies', None)
            if available_copies is not None and available_copies >= qty:
                added_item = {
                    '_id': item_id,
                    'title': title,
                    'cover': cover,
                    'quantity': qty
                }
                self.user_repository.add_to_cart(user_id, added_item, session=session)
            else:
                raise InsufficientStockError

            session.commit_transaction()
        except InsufficientStockError as e:
            print(f'Error: {e}')
            session.abort_transaction()
        finally:
            self.mongodb.end_session()

        return added_item