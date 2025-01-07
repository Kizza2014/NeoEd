from fastapi import Depends

from src.repository.redis.check_in_repository import CheckInRepository
from src.repository.redis.redis_repository import RedisRepository
from src.configs.connections.mysql import get_mysql_cnx
from src.repository.mysql.classroom import MySQLClassroomRepository


class CheckInService:
    def __init__(self, class_id: str, session_id: str):
        self.class_id = class_id
        self.session_id = session_id

    def initialize(self):
        return CheckInRepository.initialize(self.class_id, self.session_id)

    def initialize_mysql(self):
        pass

    def check_in(self, student_id: str):
        CheckInRepository(self.session_id).check_in(student_id)

    def get_attendees(self):
        return CheckInRepository(self.session_id).get_attendees()

    def destroy(self):
        CheckInRepository(self.session_id).delete_cur_session(self.class_id)

    def collect_redis(self):
        mysql = get_mysql_cnx()
        attendees = self.get_attendees()
        class_repo = MySQLClassroomRepository(mysql)
        members = [row[0] for row in class_repo.get_all_students(self.class_id)]
        members = set(members)
        absent = members.difference(attendees)
        return {
            'attend': list(attendees),
            'absent': list(absent)
        }

    def save_to_mysql(self):
