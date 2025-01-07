import json
from datetime import datetime

from mysql.connector.pooling import PooledMySQLConnection
from mysql.connector.errors import Error

from src.repository.redis.check_in_repository import CheckInRepository
from src.repository.redis.redis_repository import RedisRepository
from src.configs.connections.mysql import get_mysql_cnx
from src.repository.mysql.classroom import MySQLClassroomRepository


class CheckInService:
    def __init__(self, class_id: str = None, session_id: str = None, creator_id: str = None):
        self.class_id = class_id
        self.session_id = session_id
        self.creator_id = creator_id

    def initialize(self):
        if self.class_id is None and self.session_id is None:
            raise ValueError()
        self._initialize_mysql()
        return CheckInRepository.initialize(self.class_id, self.session_id)

    def _initialize_mysql(self):
        cnx: PooledMySQLConnection = get_mysql_cnx()
        check_in_query = """
        INSERT INTO `neoed`.`check_in_session`
        (`session_id`,
        `class_id`,
        `creator`,
        `data`,
        `started_at`,
        `done`,
        `ended_at`)
        VALUES
        (%s, %s, %s, %s, %s, %s, %s)

        """
        try:
            cur = cnx.cursor()
            cur.execute(check_in_query, (self.session_id,
                                         self.class_id,
                                         self.creator_id,
                                         json.dumps({}),
                                         datetime.now(),
                                         0,
                                         datetime.now()))
            cnx.commit()
        except Exception as e:
            cnx.rollback()
            raise e
        finally:
            cnx.close()

    def check_in(self, student_id: str):
        if student_id is None and self.session_id is None:
            raise ValueError()
        CheckInRepository(self.session_id).check_in(student_id)

    def get_attendees(self):
        if self.session_id is None:
            raise ValueError()
        return CheckInRepository(self.session_id).get_attendees()

    def destroy(self):
        if self.session_id is None and self.class_id is None:
            raise ValueError()
        CheckInRepository(self.session_id).delete_cur_session(self.class_id)

    def _collect_redis(self, mysql):
        attendees = self.get_attendees()
        class_repo = MySQLClassroomRepository(mysql)
        members = [row[0] for row in class_repo.get_all_students(self.class_id)]
        members = set(members)
        absent = members.difference(attendees)
        return {
            'attend': list(attendees),
            'absent': list(absent)
        }

    def _save_to_mysql(self):
        cnx = get_mysql_cnx()
        update_session_query = """
        UPDATE `check_in_session`
        SET
        `data` = %s,
        `ended_at` = %s,
        `done` = 1
        WHERE `session_id` = %s;

        """
        try:
            data = self._collect_redis(cnx)
            absentees = data['absent']
            user_ids_placeholder = ', '.join(['%s'] * len(absentees))
            update_absent_count_query = f"""
            UPDATE `users_classes`
            SET
            `num_session_absent` = `num_session_absent` + 1
            WHERE `user_id` in ({user_ids_placeholder}) AND `class_id` = %s;

            """
            data_str = json.dumps(data)

            cur = cnx.cursor()
            cur.execute(update_session_query, (data_str, datetime.now(), self.session_id))

            cur.execute(update_absent_count_query, (*absentees, self.class_id))

            cnx.commit()
            return True
        except Error:
            cnx.rollback()
            return False
        finally:
            cnx.close()

    def synchronize_mysql(self, max_retry: int = 5):
        count = 0
        while not self._save_to_mysql() and max_retry < 5:
            count += 1
        return True if count < 5 else False
