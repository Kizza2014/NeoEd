from src.repository.mysql.mysql_repository_interface import MysqlRepositoryInterface
from src.service.models.classroom import ClassroomCreate, ClassroomUpdate
from typing import List
from datetime import datetime
from pytz import timezone
from mysql.connector import Error as MySQLError
from src.repository.utils import generate_invitation_code


class MySQLClassroomRepository(MysqlRepositoryInterface):
    async def get_classroom_for_user(self, user_id: str) -> dict:
        cursor = self.connection.cursor
        cursor.execute(
            """
            SELECT 
                -- classroom information
                c.id, c.class_name, c.subject_name, c.class_schedule, c.description, c.created_at, 
                c.updated_at, c.owner_id,
                
                -- owner information
                c.owner_id, u.username AS owner_username, u.fullname AS owner_fullname, uc.role
            FROM (SELECT class_id, role
                  FROM users_classes
                  WHERE user_id LIKE %s  
                 ) AS uc JOIN classes AS c ON uc.class_id LIKE c.id JOIN users AS u ON c.owner_id LIKE u.id
            """,
            (user_id,)
        )
        classrooms = cursor.fetchall()
        joined_classes = [classroom for classroom in classrooms if classroom['role'] == 'student']
        owned_classes = [classroom for classroom in classrooms if classroom['role'] == 'teacher']
        return {
            'joining_classes': joined_classes,
            'teaching_classes': owned_classes
        }

    async def get_by_id(self, class_id: str) -> dict | None:
        cursor = self.connection.cursor
        cursor.execute(
            """SELECT 
                    -- classroom information
                    c.id, c.class_name, c.subject_name, c.class_schedule, c.description, 
                    c.created_at, c.updated_at,
                    
                    -- owner information
                    c.owner_id, u.username AS owner_username, u.fullname AS owner_fullname
               FROM classes AS c JOIN users AS u ON c.owner_id LIKE u.id
               WHERE c.id LIKE %s
            """,
            (class_id,)
        )
        res = cursor.fetchone()
        return res

    async def get_by_invitation_code(self, invitation_code: str) -> dict | None:
        cursor =self.connection.cursor
        cursor.execute("SELECT * FROM classes WHERE invitation_code LIKE %s", (invitation_code,))
        res = cursor.fetchone()
        if res:
            res.pop('invitation_code', None)
            return res
        return None

    async def get_invitation_code(self, class_id: str) -> str:
        cursor = self.connection.cursor
        cursor.execute("SELECT invitation_code FROM classes WHERE id LIKE %s", (class_id,))
        res = cursor.fetchone()
        return res['invitation_code'] if res else None

    async def get_owner(self, class_id: str) -> dict:
        cursor = self.connection.cursor
        cursor.execute("""SELECT u.id, u.username, u.fullname, u.email, u.birthdate, u.address, u.joined_at 
                           FROM classes AS c JOIN users AS u ON c.owner_id LIKE u.id 
                           WHERE c.id LIKE %s""", (class_id,))
        owner = cursor.fetchone()
        if not owner:
            raise MySQLError('Classroom not found')
        return owner

    async def get_user_role(self, user_id: str, class_id: str) -> str:
        cursor = self.connection.cursor
        cursor.execute("""SELECT * FROM users_classes WHERE user_id LIKE %s AND class_id LIKE %s""",
                            (user_id, class_id)
        )
        res = cursor.fetchone()
        return res['role'] if res else None

    async def create_classroom(self, new_classroom: ClassroomCreate) -> bool:
        cursor = self.connection.cursor
        invitation_code = await generate_invitation_code(new_classroom.id)
        tz = timezone('Asia/Ho_Chi_Minh')
        current_time = datetime.now(tz)
        cursor.execute(
            """INSERT INTO classes(id, class_name, subject_name, class_schedule, description, created_at, 
                                    updated_at, owner_id, invitation_code)
               VALUE(%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                new_classroom.id,
                new_classroom.class_name,
                new_classroom.subject_name,
                new_classroom.class_schedule,
                new_classroom.description,
                current_time,
                current_time,
                new_classroom.owner_id,
                invitation_code
            )
        )

        cursor.execute(
            "INSERT INTO users_classes(user_id, class_id, joined_at, role) VALUE (%s, %s, %s, 'teacher')",
            (new_classroom.owner_id, new_classroom.id, current_time)
        )

        if self.auto_commit:
            self.connection.commit()
        return cursor.rowcount > 0

    async def create_classroom_from_template(self, template, new_id: str):
        _template = template.copy()
        _template['id'] = new_id
        return await self.create_classroom(ClassroomCreate(**_template))

    async def update_by_id(self, class_id: str, new_info: ClassroomUpdate) -> bool:
        cursor = self.connection.cursor
        new_info = new_info.model_dump(exclude_unset=True)
        query_params = []
        query_values = []
        for k, v in new_info.items():
            query_params.append(f"{k} = %s")
            query_values.append(v)

        tz = timezone('Asia/Ho_Chi_Minh')
        current_time = datetime.now(tz)
        query_params.append('updated_at = %s')
        query_values.append(current_time)
        update_query = f"""UPDATE classes SET {', '.join(query_params)} WHERE id LIKE %s"""
        query_values.append(class_id)
        cursor.execute(update_query, tuple(query_values))

        if self.auto_commit:
            self.connection.commit()
        return cursor.rowcount > 0

    async def delete_by_id(self, class_id: str) -> bool:
        cursor = self.connection.cursor
        cursor.execute("DELETE FROM classes WHERE id LIKE %s", (class_id,))
        if self.auto_commit:
            self.connection.commit()
        return cursor.rowcount > 0


    # Classroom participants
    async def get_all_participants(self, class_id: str) -> List[dict]:
        cursor = self.connection.cursor
        cursor.execute("""SELECT * FROM users_classes WHERE class_id LIKE %s""", (class_id,))
        res = cursor.fetchall()
        return res

    async def add_participant(self, user_id: str, class_id: str, role: str) -> bool:
        cursor = self.connection.cursor
        tz = timezone('Asia/Ho_Chi_Minh')
        current_time = datetime.now(tz)
        cursor.execute(
            """INSERT INTO users_classes(user_id, class_id, joined_at, role) VALUE (%s, %s, %s, %s)""",
            (user_id, class_id, current_time, role)
        )
        if self.auto_commit:
            self.connection.commit()
        return cursor.rowcount > 0

    async def remove_participant(self, user_id: str, class_id: str, role: str) -> bool:
        cursor = self.connection.cursor
        self.cursor.execute(
            """DELETE FROM users_classes WHERE user_id LIKE %s AND class_id LIKE %s AND role LIKE %s""",
            (user_id, class_id, role)
        )
        if self.auto_commit:
            self.connection.commit()
        return cursor.rowcount > 0

    def get_all_students(self, class_id: str):
        cursor = self.connection.cursor()
        cursor.execute("""
                                SELECT user_id
                                FROM users_classes
                                WHERE class_id LIKE %s
                                AND users_classes.role LIKE 'student'
                                """,
                       (class_id,)
                       )
        res = cursor.fetchall()
        return res
