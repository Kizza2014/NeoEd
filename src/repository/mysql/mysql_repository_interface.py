from abc import ABC, abstractmethod
from mysql.connector.pooling import PooledMySQLConnection


class MysqlRepositoryInterface(ABC):
    def __init__(self, connection: PooledMySQLConnection, auto_commit: bool = True):
        self.connection = connection
        self.cursor = connection.cursor
        self.auto_commit = auto_commit

    # @abstractmethod
    # def get_by_id(self, item_id: str):
    #     pass
    #
    # @abstractmethod
    # def update_by_id(self, item_id: str, new_item):
    #     pass
    #
    # @abstractmethod
    # def delete_by_id(self, item_id: str):
    #     pass
    #
    # @abstractmethod
    # def insert(self, item):
    #     pass
