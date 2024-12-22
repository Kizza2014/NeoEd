from src.repository.mysql.mysql_repository_interface import MysqlRepositoryInterface
from src.service.models.classroom import ClassroomCreate, ClassroomUpdate
from src.configs.security import get_password_hash
from typing import List
from datetime import datetime


class MySQLClassroomRepository(MysqlRepositoryInterface):
    async def get_all(self) -> list[dict]:
        self.cursor.execute("""SELECT id, class_name, subject_name, owner, class_schedule, created_at, updated_at 
                               FROM classes""")
        return self.cursor.fetchall()


    async def get_by_id(self, class_id: str) -> dict | None:
        self.cursor.execute("""SELECT id, class_name, subject_name, owner, class_schedule, created_at, updated_at 
                          FROM classes 
                          WHERE id LIKE %s""",
                       (class_id,))
        return self.cursor.fetchone()


    async def update_by_id(self, class_id: str, new_info: ClassroomUpdate) -> bool:
        current_time = datetime.now()
        time_mysql_format = current_time.strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute("""
                                UPDATE classes
                                SET
                                    class_name = %s,
                                    subject_name = %s,
                                    class_schedule = %S,
                                    updated_at = %s,
                                WHERE id LIKE %s
                                """,
                       (
                           new_info.class_name,
                           new_info.subject_name,
                           new_info.class_schedule,
                           time_mysql_format,
                           class_id,
                       )
        )
        if self.auto_commit:
            self.connection.commit()
        return self.cursor.rowcount() > 0


    async def delete_by_id(self, class_id: str) -> bool:
        self.cursor.execute("DELETE FROM users_classes WHERE class_id LIKE %s", (class_id,))
        self.cursor.execute("DELETE FROM classes WHERE id LIKE %s", (class_id,))
        if self.auto_commit:
            self.connection.commit()
        return self.cursor.rowcount > 0


    async def create_classroom(self, new_classroom: ClassroomCreate) -> bool:
        current_time = datetime.now()
        time_mysql_format = current_time.strftime('%Y-%m-%d %H:%M:%S')
        hashed_password = get_password_hash(new_classroom.password)

        self.cursor.execute("""INSERT INTO classes(id, class_name, subject_name, class_schedule, created_at, updated_at, owner, hashed_password)
                          VALUE(%s, %s, %s, %s, %s, %s, %s, %s)""",
                       (
                           new_classroom.id,
                           new_classroom.class_name,
                           new_classroom.subject_name,
                           new_classroom.class_schedule,
                           time_mysql_format,
                           time_mysql_format,
                           new_classroom.owner,
                           hashed_password
                       )
        )

        if self.auto_commit:
            self.connection.commit()
        return self.cursor.rowcount > 0



# Participants
    async def get_all_participants(self, class_id: str) -> List[dict]:
        self.cursor.execute("""
                        SELECT username, joined_at
                        FROM users_classes
                        WHERE class_id LIKE %s
                        """,
                       (class_id,)
        )
        res = self.cursor.fetchall()
        return res


    async def add_participant(self, username: str, class_id: str) -> bool:
        current_time = datetime.now()
        time_mysql_format = current_time.strftime('%Y-%m-%d %H:%M:%S')

        self.cursor.execute("""INSERT INTO users_classes 
                          VALUE (%s, %s, %s)
                        """,
                       (username, class_id, time_mysql_format)
        )
        if self.auto_commit:
            self.connection.commit()
        return self.cursor.rowcount > 0


    async def remove_participant(self, username: str, class_id: str) -> bool:
        self.cursor.execute("""
                                DELETE FROM users_classes
                                WHERE username LIKE %s AND class_id LIKE %s
                            """,
                            (username, class_id,)
        )
        if self.auto_commit:
            self.connection.commit()
        return self.cursor.rowcount > 0