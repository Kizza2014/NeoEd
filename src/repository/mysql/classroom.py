from src.repository.mysql.mysql_repository_interface import MysqlRepositoryInterface
from src.configs.utils import fetch_all_as_dict, fetch_one_as_dict
from src.service.models import Classroom
from mysql.connector import Error


class ClassroomRepository(MysqlRepositoryInterface):
    def get_all(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM classes")
        res = fetch_all_as_dict(cursor)
        return res


    def get_by_id(self, item_id: str):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM classes WHERE id LIKE %s", (item_id,))
        res = fetch_one_as_dict(cursor)
        return res


    def update_by_id(self, item_id: str, new_item: Classroom):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                                    UPDATE classes 
                                    SET
                                        id = %s,
                                        class_name = %s,
                                        semester = %s,
                                        room_id = %s,
                                        subject_name = %s,
                                        class_schedule = %S,
                                        created_at = %s,
                                        updated_at = %s,
                                    WHERE id LIKE %s
                                    """,
                           (
                               new_item.id,
                               new_item.class_name,
                               new_item.semester,
                               new_item.room_id,
                               new_item.subject_name,
                               new_item.class_schedule,
                               new_item.created_at,
                               new_item.updated_at,
                               item_id,
                           )
                           )
        except Error:
            return False
        self.conn.commit()
        return cursor.rowcount() > 0


    def delete_by_id(self, item_id: str):
        cursor = self.conn.cursor()
        cursor.execute("DELETE from classes WHERE id LIKE %s", (item_id,))
        self.conn.commit()
        return cursor.rowcount() > 0


    def insert(self, item: Classroom):
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO classes VALUE(%s, %s, %s, %s, %s, %s, %s, %s)",
                           (
                               item.id,
                               item.class_name,
                               item.semester,
                               item.room_id,
                               item.subject_name,
                               item.class_schedule,
                               item.created_at,
                               item.updated_at,
                           )
            )
        except Error:
            return False
        self.conn.commit()
        return cursor.rowcount() > 0