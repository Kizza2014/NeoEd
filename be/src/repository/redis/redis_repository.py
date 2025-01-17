from src.configs.connections.redis import get_redis


class RedisRepository:
    def __init__(self, user_id: str,
                 access_exp_minutes=15,
                 refresh_exp_days=7):
        self.user_id = user_id
        self.access_exp_minutes = access_exp_minutes
        self.refresh_exp_days = refresh_exp_days

    def save_access_token(self,
                          access_token: str):
        redis_client = get_redis()
        try:
            redis_client.set(f"access_token:{self.user_id}", access_token, ex=self.access_exp_minutes * 60)
        except Exception as e:
            raise e
        finally:
            redis_client.close()

    def save_refresh_token(self,
                           refresh_token: str):
        redis_client = get_redis()
        try:
            redis_client.set(f"refresh_token:{self.user_id}", refresh_token, ex=self.refresh_exp_days * 24 * 60 * 60)
        except Exception as e:
            raise e
        finally:
            redis_client.close()

    def get_access_token(self) -> str:
        redis_client = get_redis()
        try:
            return redis_client.get(f"access_token:{self.user_id}")
        except Exception as e:
            raise e
        finally:
            redis_client.close()

    def get_refresh_token(self) -> str:
        redis_client = get_redis()
        try:
            return redis_client.get(f"refresh_token:{self.user_id}")
        except Exception as e:
            raise e
        finally:
            redis_client.close()

    def delete_access_token(self):
        redis_client = get_redis()
        try:
            redis_client.delete(f"access_token:{self.user_id}")
        except Exception as e:
            raise e
        finally:
            redis_client.close()

    def delete_refresh_token(self):
        redis_client = get_redis()
        try:
            redis_client.delete(f"refresh_token:{self.user_id}")
        except Exception as e:
            raise e
        finally:
            redis_client.close()
