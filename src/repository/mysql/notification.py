from src.repository.mysql import MysqlRepositoryInterface


class NotificationRepository(MysqlRepositoryInterface):
    def get_by_id(self, item_id: str):
        pass

    def update_by_id(self, item_id: str, new_item):
        pass

    def delete_by_id(self, item_id: str):
        pass

    def insert(self, item):
        pass