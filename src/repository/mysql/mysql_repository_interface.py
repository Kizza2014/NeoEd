from mysql.connector.pooling import PooledMySQLConnection


class MysqlRepositoryInterface:
    def __init__(self, connection: PooledMySQLConnection, auto_commit: bool = True):
        self.connection = connection
        self.cursor = connection.cursor
        self.auto_commit = auto_commit

