from abc import ABC, abstractmethod


class MysqlRepositoryInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_by_id(self, item_id: str):
        pass

    @abstractmethod
    def update_by_id(self, item_id: str, new_item):
        pass

    @abstractmethod
    def delete_by_id(self, item_id: str):
        pass

    @abstractmethod
    def insert(self, item):
        pass
