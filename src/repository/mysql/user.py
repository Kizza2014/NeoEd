from src.service.models.user import BaseUser
from src.configs.security import get_password_hash
from src.repository.mysql.mysql_repository_interface import MysqlRepositoryInterface
from src.configs.utils import fetch_all_as_dict, fetch_one_as_dict
from mysql.connector import Error
from typing import List
from src.service.models.user import UserInfo, UserUpdate
from src.service.models.authentication import UserCreate
from datetime import datetime


class UserRepository(MysqlRepositoryInterface):
    def get_all(self) -> List[UserInfo]:
        cursor = self.conn.cursor()
        cursor.execute("""SELECT id, user_name, gender, birthdate, user_role, email, address, joined_at 
                          FROM users
                       """)
        query_result = fetch_all_as_dict(cursor)
        return [UserInfo(**info) for info in query_result]


    def get_by_id(self, user_id: str) -> BaseUser | None:
        cursor = self.conn.cursor()
        cursor.execute("""SELECT * 
                          FROM users 
                          WHERE id LIKE %s
                        """, (user_id,))
        query_result = fetch_one_as_dict(cursor)
        if query_result is None:
            return None
        return BaseUser(**query_result)


    def get_info_by_id(self, user_id: str) -> UserInfo | None:
        cursor = self.conn.cursor()
        cursor.execute("""SELECT id, user_name, gender, birthdate, user_role, email, address, joined_at 
                          FROM users 
                          WHERE id LIKE %s
                        """, (user_id,))
        query_result = fetch_one_as_dict(cursor)
        return UserInfo(**query_result)


    def update_by_id(self, user_id: str, new_info: UserUpdate):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                            UPDATE users 
                            SET
                                user_name = %s,
                                gender = %s,
                                birthdate = %s,
                                user_role = %s,
                                address = %S,
                                email = %s,
                            WHERE id LIKE %s
                            """,
                           (
                               new_info.user_name,
                               new_info.gender,
                               new_info.birthdate,
                               new_info.user_role,
                               new_info.address,
                               new_info.email,
                               user_id,
                           )
            )
        except Error:
            return False
        self.conn.commit()
        return cursor.rowcount > 0


    def delete_by_id(self, user_id: str):
        cursor = self.conn.cursor()
        cursor.execute("DELETE from users WHERE id LIKE %s", (user_id,))
        self.conn.commit()
        return cursor.rowcount > 0


    def insert(self, new_user: UserCreate):
        cursor = self.conn.cursor()
        current_time = datetime.now()
        time_mysql_format = current_time.strftime('%Y-%m-%d %H:%M:%S')
        password_hash = get_password_hash(new_user.user_passwd)

        try:
            cursor.execute("INSERT INTO users VALUE(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (
                               new_user.id,
                               new_user.user_name,
                               new_user.gender,
                               new_user.birthdate,
                               new_user.user_role,
                               new_user.address,
                               new_user.email,
                               password_hash,
                               time_mysql_format,
                           )
            )
        except Error:
            return False
        self.conn.commit()
        return cursor.rowcount > 0

    def change_user_password(self, user_id: str, new_password: str):
        cursor = self.conn.cursor()
        password_hash = get_password_hash(new_password)
        cursor.execute("""UPDATE users 
                          SET user_passwd = %s
                          WHERE id LIKE %s
                        """, (password_hash, user_id)
                       )
        self.conn.commit()
        return cursor.rowcount > 0