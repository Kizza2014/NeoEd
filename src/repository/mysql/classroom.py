from src.repository.mysql.mysql_repository_interface import MysqlRepositoryInterface
from src.service.models.classroom import ClassroomCreate, ClassroomUpdate
from src.configs.security import get_password_hash
from typing import List
from datetime import datetime


class MySQLClassroomRepository(MysqlRepositoryInterface):

    # GET
    async def get_all(self) -> list[dict]:
        self.cursor.execute("""SELECT id, class_name, subject_name, owner, class_schedule, created_at, updated_at 
                               FROM classes""")
        return self.cursor.fetchall()


    async def get_classes_of_users(self, username: str) -> List[dict]:
        self.cursor.execute(
            """
            SELECT c.id, c.class_name, c.subject_name, c.owner, c.class_schedule, c.created_at, c.updated_at
            FROM (SELECT *
                  FROM users_classes
                  WHERE username LIKE %s  
                 ) AS uc JOIN classes AS c ON uc.class_id LIKE c.id
            """,
            (username,)
        )
        return self.cursor.fetchall()


    async def get_by_id(self, class_id: str) -> dict | None:
        self.cursor.execute("""SELECT id, class_name, subject_name, owner, class_schedule, created_at, updated_at 
                          FROM classes 
                          WHERE id LIKE %s""",
                       (class_id,))
        return self.cursor.fetchone()


    # CREATE
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


    # UPDATE
    async def update_by_id(self, class_id: str, new_info: ClassroomUpdate) -> bool:
        new_info = new_info.model_dump(exclude_unset=True)
        query_params = []
        query_values = []
        for k, v in new_info.items():
            query_params.append(f"{k} = %s")
            query_values.append(v)

        current_time = datetime.now()
        time_mysql_format = current_time.strftime('%Y-%m-%d %H:%M:%S')
        query_params.append('updated_at = %s')
        query_values.append(time_mysql_format)
        update_query = f"""
                                UPDATE classes 
                                SET {', '.join(query_params)}
                                WHERE id LIKE %s
                               """
        query_values.append(class_id)
        self.cursor.execute(update_query, tuple(query_values))

        if self.auto_commit:
            self.connection.commit()
        return self.cursor.rowcount > 0


    # DELETE
    async def delete_by_id(self, class_id: str) -> bool:
        self.cursor.execute("DELETE FROM users_classes WHERE class_id LIKE %s", (class_id,))
        self.cursor.execute("DELETE FROM classes WHERE id LIKE %s", (class_id,))
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