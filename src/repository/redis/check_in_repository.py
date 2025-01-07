import uuid

from src.configs.connections.redis import get_redis


class CheckInRepository:
    def __init__(self, session_id: str = None):
        self.session_id = session_id

    @staticmethod
    def initialize(class_id: str, session_id=None):
        if session_id is None:
            session_id = "ss-" + str(uuid.uuid4())

        redis = get_redis()
        try:
            redis.set(f"cur_ci_sess:{class_id}", session_id)
            return session_id
        except Exception as e:
            raise e
        finally:
            redis.close()

    def check_in(self, user_id: str):
        if self.session_id is None:
            raise ValueError("Session ID can not be None.")
        redis = get_redis()
        try:
            redis.sadd(f"ci:{self.session_id}", user_id)
        except Exception as e:
            raise e
        finally:
            redis.close()

    @staticmethod
    def get_current_session(class_id: str):
        redis = get_redis()
        try:
            session_id = redis.get(f"cur_ci_sess:{class_id}")
            return session_id
        except Exception as e:
            raise e
        finally:
            redis.close()

    def get_attendees(self):
        redis = get_redis()
        try:
            attendees = redis.smembers(f"ci:{self.session_id}")
            return attendees
        except Exception as e:
            raise e
        finally:
            redis.close()

    def delete_cur_session(self, class_id: str):
        redis = get_redis()
        try:
            redis.delete(f"cur_ci_sess:{class_id}")
            redis.delete(f"ci:{self.session_id}")
        except Exception as e:
            raise e
        finally:
            redis.close()