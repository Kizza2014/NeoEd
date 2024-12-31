from redis import Redis, ConnectionPool

CONNECTION_POOL = ConnectionPool(
    host='redis-16309.c290.ap-northeast-1-2.ec2.redns.redis-cloud.com',
    port=16309,
    decode_responses=True,
    username="default",
    password="intHeCHpDxhOdfK9XmN0UNUwYI3tLmg2",
)


def get_redis():
    try:
        redis = Redis(connection_pool=CONNECTION_POOL)
        yield redis
    except ConnectionError:
        pass