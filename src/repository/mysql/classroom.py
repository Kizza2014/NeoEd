from src.repository.mysql.mysql_repository_interface import MysqlRepositoryInterface
from src.service.models.classroom import ClassroomCreate, ClassroomUpdate
from src.configs.security import get_password_hash, verify_password
from typing import List
from datetime import datetime
from mysql.connector import Error as MySQLError


class MySQLClassroomRepository(MysqlRepositoryInterface):

    # GET
    async def get_all(self) -> list[dict]:
        self.cursor.execute("""SELECT id, class_name, subject_name, owner_id, class_schedule, created_at, updated_at 
                               FROM classes""")
        return self.cursor.fetchall()


    async def get_all_classroom_of_user(self, user_id: str) -> List[dict]:
        self.cursor.execute(
            """
            SELECT c.id, c.class_name, c.subject_name, c.owner_id, c.class_schedule, 
                            c.description, c.created_at, c.updated_at, c.require_password
            FROM (SELECT *
                  FROM users_classes
                  WHERE username LIKE %s  
                 ) AS uc JOIN classes AS c ON uc.class_id LIKE c.id
            """,
            (user_id,)
        )
        return self.cursor.fetchall()


    async def get_by_id(self, class_id: str) -> dict | None:
        self.cursor.execute("""SELECT id, class_name, subject_name, owner_id, class_schedule, 
                                        description, created_at, updated_at, require_password 
                          FROM classes 
                          WHERE id LIKE %s""",
                       (class_id,))
        return self.cursor.fetchone()


    async def get_owner_id(self, class_id: str) -> str:
        self.cursor.execute("SELECT owner_id FROM classes WHERE id LIKE %s", (class_id,))
        owner = self.cursor.fetchone()
        if not owner:
            raise MySQLError('Classroom not found')
        return owner['owner_id']


    # CREATE
    async def create_classroom(self, new_classroom: ClassroomCreate) -> bool:
        hashed_password = get_password_hash(new_classroom.password) if new_classroom.password else None

        self.cursor.execute("""INSERT INTO classes(id, class_name, subject_name, class_schedule, description, 
                                                    created_at, updated_at, owner_id, hashed_password, require_password)
                              VALUE(%s, %s, %s, %s, %s, NOW(), NOW(), %s, %s, %s)""",
                                (
                                    new_classroom.id,
                                    new_classroom.class_name,
                                    new_classroom.subject_name,
                                    new_classroom.class_schedule,
                                    new_classroom.description,
                                    new_classroom.owner_id,
                                    hashed_password,
                                    new_classroom.require_password
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


    async def add_participant(self, user_id: str, class_id: str) -> bool:
        self.cursor.execute("""INSERT INTO users_classes 
                          VALUE (%s, %s, NOW())
                        """,
                       (user_id, class_id)
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


    # SECURITY
    async def verify_password(self, class_id: str, password: str) -> bool:
        self.cursor.execute("""SELECT hashed_password, require_password 
                               FROM classes 
                               WHERE id LIKE %s""",
                            (class_id,)
        )
        security_infor = self.cursor.fetchone()
        if not security_infor['require_password']:
            return True
        return verify_password(password, security_infor['hashed_password'])