from redis import Redis, ConnectionPool

CONNECTION_POOL = ConnectionPool(
    host='redis-14584.crce178.ap-east-1-1.ec2.redns.redis-cloud.com',
    port=14584,
    decode_responses=True,
    username="default",
    password="AKF2fi41cLDM3zmsv09jK7myKtSqfe3e",
)


def get_redis():
    try:
        redis = Redis(connection_pool=CONNECTION_POOL)
        yield redis
    except ConnectionError:
        pass
