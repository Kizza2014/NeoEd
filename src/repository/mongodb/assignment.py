from src.repository.mysql.mysql_repository_interface import MysqlRepositoryInterface
from src.service.models import Assignment
from src.configs.utils import fetch_all_as_dict, fetch_one_as_dict
from mysql.connector import Error


class AssignmentRepository(MysqlRepositoryInterface):
    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM assignments")
        res = fetch_all_as_dict(cursor)
        return res


    def get_by_id(self, item_id: str):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM assignments WHERE id LIKE %s", (item_id,))
        res = fetch_one_as_dict(cursor)
        return res


    def update_by_id(self, item_id: str, new_item: Assignment):
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                                    UPDATE assignments 
                                    SET
                                        id = %s,
                                        title = %s,
                                        class_id = %s,
                                        author = %s,
                                        descriptions = %s,
                                        created_at = %S,
                                        updated_at = %s,
                                        start_at = %s,
                                        end_at = %s
                                    WHERE id LIKE %s
                                    """,
                           (
                               new_item.id,
                               new_item.title,
                               new_item.class_id,
                               new_item.author,
                               new_item.descriptions,
                               new_item.created_at,
                               new_item.updated_at,
                               new_item.start_at,
                               new_item.end_at,
                               item_id,
                           )
            )
        except Error:
            return False
        self.connection.commit()
        return cursor.rowcount() > 0


    def delete_by_id(self, item_id: str):
        cursor = self.connection.cursor()
        cursor.execute("DELETE from users WHERE id LIKE %s", (item_id,))
        self.connection.commit()
        return cursor.rowcount() > 0


    def insert(self, new_item: Assignment):
        cursor = self.connection.cursor()
        try:
            cursor.execute("INSERT INTO assignments VALUE(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (
                               new_item.id,
                               new_item.title,
                               new_item.class_id,
                               new_item.author,
                               new_item.descriptions,
                               new_item.created_at,
                               new_item.updated_at,
                               new_item.start_at,
                               new_item.end_at,
                           )
            )
        except Error:
            return False
        self.connection.commit()
        return cursor.rowcount() > 0