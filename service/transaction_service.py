from config import MongoDBManager
from repository import UserRepository, BookRepository, TransactionRepository
from errors import InsufficientFundsError, InsufficientStockError
from datetime import datetime


class TransactionService:
    def __init__(
            self,
            mongodb: MongoDBManager,
            user_repository: UserRepository,
            book_repository: BookRepository,
            transaction_repository: TransactionRepository
    ):
        self.mongodb = mongodb
        self.user_repository = user_repository
        self.book_repository = book_repository
        self.transaction_repository = transaction_repository

    def book_transaction(self, transaction_info: dict):
        user_id = transaction_info['user_id']
        items = transaction_info['items']
        if len(items) > 0:
            total_amount = transaction_info['total_amount']
            date_created = datetime.now().isoformat()

            trans = {
                '_id': str(user_id) + '_' + date_created,
                'user_id': user_id,
                'items': items,
                'total_amount': total_amount,
                'date_created': date_created
            }

            session = self.mongodb.get_session()
            session.start_transaction()
            try:
                for item in items:
                    item_id = item['_id']
                    quantity = item['quantity']
                    item_in_db = self.book_repository.get_by_id(item_id, session=session)
                    available_copies = item_in_db['available_copies']

                    if available_copies < quantity:
                        raise InsufficientStockError

                    self.user_repository.add_bought_books(user_id, item, session=session)
                    self.book_repository.reduce_quantity(item_id, quantity, session=session)

                user_in_db = self.user_repository.get_by_id(user_id)

                if user_in_db['balance'] < total_amount:
                    raise InsufficientFundsError

                self.user_repository.reduce_balance(user_id, total_amount, session=session)
                self.user_repository.clear_cart(user_id, session=session)

                # confirm that transaction is succeeded
                trans['status'] = 'succeed'
                self.transaction_repository.insert(trans, session=session)
                self.user_repository.add_transaction(user_id, trans, session=session)

                session.commit_transaction()
            except InsufficientStockError as e:
                session.abort_transaction()
                trans['status'] = 'failed'
                trans['reason'] = 'Insufficient stock error'
                raise e
            except InsufficientFundsError as e:
                session.abort_transaction()
                trans['status'] = 'failed'
                trans['reason'] = 'Insufficient balance error'
                raise e
            except Exception as e:
                session.abort_transaction()
                trans['status'] = 'failed'
                trans['reason'] = 'Unexpected error'
                raise e
            finally:
                if trans['status'] == 'failed':
                    self.user_repository.add_transaction(user_id, trans)
                    self.transaction_repository.insert(trans)
                self.mongodb.end_session()