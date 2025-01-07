from src.service.models.exceptions import PasswordValidationError, UsernameValidationError
from src.service.authentication.utils import get_password_hash
from src.repository.mysql import MysqlRepositoryInterface
from typing import List
from src.service.models.user import UserCreate, UserUpdate
from datetime import datetime


class UserRepository(MysqlRepositoryInterface):
    async def get_by_id(self, user_id: str):
        query = """
        SELECT * FROM users WHERE id = %s
        """
        self.cursor.execute(query, (user_id, ))
        row = self.cursor.fetchone()
        return row

    async def get_all(self) -> List[dict]:
        self.cursor.execute("""SELECT username, fullname, gender, birthdate, email, address, joined_at 
                                FROM users
                       """)
        query_result = self.cursor.fetchall()
        return query_result

    async def get_by_username(self, username: str) -> dict | None:
        self.cursor.execute("""SELECT *
                               FROM users 
                               WHERE username LIKE %s
                        """, (username,))
        user = self.cursor.fetchone()
        return user

    async def create_user(self, new_user: UserCreate) -> bool:
        current_time = datetime.now()
        time_mysql_format = current_time.strftime('%Y-%m-%d %H:%M:%S')

        if len(new_user.username) > 50 or not new_user.username.isalnum():
            raise UsernameValidationError

        if len(new_user.password) < 8 or not any(char.isdigit() for char in new_user.password):
            raise PasswordValidationError
        password_hash = get_password_hash(new_user.password)
        query = """
        INSERT INTO `neoed`.`users`
        (`id`,
        `username`,
        `fullname`,
        `gender`,
        `birthdate`,
        `email`,
        `address`,
        `hashed_password`,
        `joined_at`)
        VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s);

        """

        self.cursor.execute(query,
                            (
                                new_user.user_id,
                                new_user.username,
                                new_user.fullname,
                                new_user.gender,
                                new_user.birthdate,
                                new_user.email,
                                new_user.address,
                                password_hash,
                                time_mysql_format,
                            )
        )
        if self.auto_commit:
            self.connection.commit()
        return self.cursor.rowcount > 0

    async def update_by_username(self, username: str, new_info: UserUpdate) -> bool:
        update_fields = []
        update_values = []

        if new_info.fullname is not None and len(new_info.fullname) > 0:
            update_fields.append("fullname = %s")
            update_values.append(new_info.fullname)
        if new_info.gender is not None:
            update_fields.append("gender = %s")
            update_values.append(new_info.gender)
        if new_info.birthdate is not None:
            update_fields.append("birthdate = %s")
            update_values.append(new_info.birthdate)
        if new_info.email is not None and len(new_info.email) > 0:
            update_fields.append("email = %s")
            update_values.append(new_info.email)
        if new_info.address is not None and len(new_info.address) > 0:
            update_fields.append("address = %s")
            update_values.append(new_info.address)

        update_query = f"""
                        UPDATE users 
                        SET {', '.join(update_fields)}
                        WHERE username LIKE %s
                       """
        update_values.append(username)
        self.cursor.execute(update_query, tuple(update_values))

        if self.auto_commit:
            self.connection.commit()
        return self.cursor.rowcount > 0

    async def delete_by_username(self, username: str) -> bool:
        self.cursor.execute("DELETE FROM users_classes WHERE username LIKE %s", (username,))
        self.cursor.execute("DELETE FROM users WHERE username LIKE %s", (username,))
        if self.auto_commit:
            self.connection.commit()
        return self.cursor.rowcount > 0

