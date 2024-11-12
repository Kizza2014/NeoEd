from src.repository.mysql.mysql_repository_interface import MysqlRepositoryInterface
from src.configs.utils import fetch_as_dict, fetch_one_as_dict
from mysql.connector import Error
from src.service.models import BaseUser


class UserRepository(MysqlRepositoryInterface):
    def get_all(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users")
        res = fetch_as_dict(cursor)
        return res


    def get_by_id(self, item_id: str):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id LIKE %s", (item_id,))
        res = fetch_one_as_dict(cursor)
        return res


    def update_by_id(self, item_id: str, new_item: BaseUser):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                            UPDATE users 
                            SET
                                id = %s,
                                user_name = %s,
                                gender = %s,
                                birthdate = %s,
                                user_role = %s,
                                address = %S,
                                email = %s,
                                user_passwd = %s,
                                joined_at = %s
                            WHERE id LIKE %s
                            """,
                           (
                               new_item.id,
                               new_item.user_name,
                               new_item.gender,
                               new_item.birthdate,
                               new_item.user_role,
                               new_item.address,
                               new_item.email,
                               new_item.user_passwd,
                               new_item.joined_at,
                               item_id,
                           )
            )
        except Error:
            return False
        self.conn.commit()
        return cursor.rowcount() > 0


    def delete_by_id(self, item_id: str):
        cursor = self.conn.cursor()
        cursor.execute("DELETE from users WHERE id LIKE %s", (item_id,))
        self.conn.commit()
        return cursor.rowcount() > 0


    def insert(self, item: BaseUser):
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO users VALUE(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (
                               item.id,
                               item.user_name,
                               item.gender,
                               item.birthdate,
                               item.user_role,
                               item.address,
                               item.email,
                               item.user_passwd,
                               item.joined_at,
                           )
            )
        except Error:
            return False
        self.conn.commit()
        return cursor.rowcount() > 0